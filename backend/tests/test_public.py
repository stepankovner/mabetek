import uuid
import pytest
from sqlalchemy import select, func
from app.models import Lead, Notification, Rental

def send(client, payload, key=None):
    return client.post("/api/leads", json=payload, headers={"Idempotency-Key": key or str(uuid.uuid4())})

def test_health_and_public_settings(setup):
    client, _, _ = setup
    assert client.get("/api/health/ready").status_code == 200
    data = client.get("/api/config").json()
    assert data["leads_enabled"] is True
    assert "secret_key" not in data
    assert "admin_password_hash" not in data

def test_lead_and_notification_are_persisted(setup, payload):
    client, sessions, _ = setup
    response = send(client, payload)
    assert response.status_code == 201
    assert set(response.json()) == {"id"}
    with sessions() as db:
        lead = db.scalar(select(Lead))
        assert lead.name == payload["name"]
        assert lead.privacy_version == "test-v1"
        assert lead.status == "new"
        assert db.scalar(select(func.count()).select_from(Notification)) == 1
    assert client.get("/api/leads").status_code == 405

@pytest.mark.parametrize("change", [
    {"name": " "}, {"name": "x" * 101}, {"contact": "garbage"},
    {"contact": "a\nb@example.com"}, {"service": "unknown"},
    {"consent": False}, {"message": "x" * 4001}, {"unexpected": "value"},
])
def test_invalid_leads_not_saved(setup, payload, change):
    client, sessions, _ = setup
    response = send(client, payload | change)
    assert response.status_code == 422
    with sessions() as db:
        assert db.scalar(select(func.count()).select_from(Lead)) == 0

def test_required_consent_and_idempotency_key(setup, payload):
    client, _, _ = setup
    del payload["consent"]
    assert send(client, payload).status_code == 422
    assert client.post("/api/leads", json=payload).status_code == 422

@pytest.mark.parametrize("contact", ["+7 (914) 123-45-67", "user@example.org"])
def test_contact_formats(setup, payload, contact):
    assert send(setup[0], payload | {"contact": contact}).status_code == 201

def test_idempotent_retry_and_conflict(setup, payload):
    client, sessions, _ = setup
    key = str(uuid.uuid4())
    first = send(client, payload, key)
    assert send(client, payload, key).json() == first.json()
    assert send(client, payload | {"message": "Different"}, key).status_code == 409
    with sessions() as db:
        assert db.scalar(select(func.count()).select_from(Lead)) == 1

def test_rate_limit_and_spoofed_forwarding(setup, payload):
    client, _, _ = setup
    for _ in range(3):
        assert send(client, payload).status_code == 201
    response = client.post("/api/leads", json=payload, headers={
        "Idempotency-Key": str(uuid.uuid4()), "X-Forwarded-For": "8.8.8.8"})
    assert response.status_code == 429
    assert "Retry-After" in response.headers

def test_disabled_collection(setup, payload):
    client, sessions, settings = setup
    settings.leads_enabled = False
    assert send(client, payload).status_code == 503
    with sessions() as db:
        assert db.scalar(select(func.count()).select_from(Lead)) == 0

def test_catalog_publication_filters_and_details(setup):
    client, sessions, _ = setup
    with sessions() as db:
        db.add_all([
            Rental(slug="office", title="Офис", kind="office", published=True, available=True),
            Rental(slug="warehouse", title="Склад", kind="warehouse", published=True, available=True),
            Rental(slug="draft", title="Черновик", kind="office", published=False, available=True),
            Rental(slug="occupied", title="Занято", kind="office", published=True, available=False),
        ])
        db.commit()
    assert len(client.get("/api/rentals").json()) == 3
    data = client.get("/api/rentals?kind=office&available=true").json()
    assert [r["slug"] for r in data] == ["office"]
    assert client.get("/api/rentals/office").json()["title"] == "Офис"
    assert client.get("/api/rentals/draft").status_code == 404
    assert client.get("/api/rentals/missing").status_code == 404
    assert client.get("/api/rentals?kind=invalid").status_code == 422
