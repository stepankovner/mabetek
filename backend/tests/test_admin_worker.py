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
