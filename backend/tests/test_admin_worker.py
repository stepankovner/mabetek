from sqlalchemy import select
from app.models import Lead, Notification
from app.notifications import deliver_pending
from test_public import send

def test_admin_requires_authentication(setup):
    client, _, _ = setup
    response = client.get("/admin/lead/list", follow_redirects=False)
    assert response.status_code in (302, 303, 307)
    assert "/login" in response.headers["location"]

def test_admin_login_logout_and_origin(setup):
    client, _, _ = setup
    assert client.post("/admin/login", data={"username":"admin", "password":"wrong"},
        headers={"Origin":"http://testserver"}).status_code == 400
    assert client.post("/admin/login", data={"username":"admin", "password":"test-password-long"},
        headers={"Origin":"https://evil.example"}).status_code == 403
    response = client.post("/admin/login", data={"username":"admin", "password":"test-password-long"},
        headers={"Origin":"http://testserver"})
    assert response.status_code == 200
    assert client.get("/admin/lead/list").status_code == 200
    assert client.get("/admin/rental/list").status_code == 200
    client.get("/admin/logout")
    assert client.get("/admin/lead/list", follow_redirects=False).status_code in (302, 303, 307)

def test_email_failure_retry_and_success(setup, payload):
    client, sessions, settings = setup
    send(client, payload)
    def fail(*_):
        raise OSError("SMTP unavailable")
    deliver_pending(sessions, settings, send_email=fail)
    with sessions() as db:
        job = db.scalar(select(Notification))
        assert job.sent_at is None
        assert job.attempts == 1
        assert db.scalar(select(Lead)) is not None
        job.next_attempt_at = 0
        db.commit()
    sent = []
    deliver_pending(sessions, settings, send_email=lambda *args: sent.append(args))
    deliver_pending(sessions, settings, send_email=lambda *args: sent.append(args))
    assert len(sent) == 1
    with sessions() as db:
        assert db.scalar(select(Notification)).sent_at is not None

def login(client):
    return client.post("/admin/login", data={"username": "admin", "password": "test-password-long"},
                       headers={"Origin": "http://testserver"})

def test_admin_creates_and_unpublishes_rental(setup):
    client, sessions, _ = setup
    login(client)
    data = {"save": "Save", "slug": "new-office", "title": "Новый офис", "kind": "office", "building": "Здание 2",
            "description": "Офис", "area": "25", "floor": "2", "monthly_price": "", "image_path": "",
            "published": "y", "available": "y"}
    response = client.post("/admin/rental/create", data=data, headers={"Origin": "http://testserver"})
    assert response.status_code == 200
    assert client.get("/api/rentals/new-office").status_code == 200
    from app.models import Rental
    with sessions() as db:
        identifier = db.scalar(select(Rental.id))
    data.pop("published")
    response = client.post(f"/admin/rental/edit/{identifier}", data=data, headers={"Origin": "http://testserver"})
    assert response.status_code == 200
    assert client.get("/api/rentals/new-office").status_code == 404

def test_admin_updates_only_lead_workflow(setup, payload):
    client, sessions, _ = setup
    identifier = send(client, payload).json()["id"]
    login(client)
    response = client.post(f"/admin/lead/edit/{identifier}",
        data={"save": "Save", "status": "in_progress", "internal_note": "Связаться завтра", "name": "Tampered"},
        headers={"Origin":"http://testserver"})
    assert response.status_code == 200
    with sessions() as db:
        lead = db.get(Lead, identifier)
        assert lead.status == "in_progress"
        assert lead.name == payload["name"]
        assert lead.internal_note == "Связаться завтра"

def test_admin_login_rate_limit(setup):
    client, _, _ = setup
    for _ in range(10):
        assert client.post("/admin/login", data={"username":"admin", "password":"wrong"},
            headers={"Origin":"http://testserver"}).status_code == 400
    assert login(client).status_code == 429

def test_foreign_origin_cannot_modify_authenticated_admin(setup):
    client, _, _ = setup
    login(client)
    for headers in [{}, {"Origin":"https://attacker.example"}]:
        assert client.post("/admin/rental/create", data={}, headers=headers).status_code == 403

def test_worker_respects_retry_schedule(setup, payload):
    client, sessions, settings = setup
    send(client, payload)
    import time
    with sessions() as db:
        db.scalar(select(Notification)).next_attempt_at = time.time() + 3600
        db.commit()
    sent = []
    deliver_pending(sessions, settings, send_email=lambda *args: sent.append(args))
    assert sent == []

def test_notification_error_redacts_sensitive_message(setup, payload):
    client, sessions, settings = setup
    send(client, payload)
    def fail(*_):
        raise RuntimeError("secret-SMTP-password and customer@example.com")
    deliver_pending(sessions, settings, send_email=fail)
    with sessions() as db:
        assert db.scalar(select(Notification)).last_error == "RuntimeError"

def test_session_cookie_and_password_rotation(setup):
    client, _, settings = setup
    response = login(client)
    cookies = [r.headers.get("set-cookie", "") for r in [*response.history, response]]
    assert any("httponly" in cookie.lower() and "samesite=strict" in cookie.lower() for cookie in cookies)
    from argon2 import PasswordHasher
    settings.admin_password_hash = PasswordHasher().hash("replacement-password")
    assert client.get("/admin/lead/list", follow_redirects=False).status_code in (302, 303, 307)
