from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.db import get_session
from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _create_user(client: TestClient, email: str, name: str) -> uuid.UUID:
    response = client.post("/users", json={"email": email, "name": name})
    assert response.status_code == 201
    return uuid.UUID(response.json()["id"])


def _headers(user_id: uuid.UUID) -> dict[str, str]:
    return {"X-User-Id": str(user_id)}


def test_agency_multi_tenant_flow(client: TestClient) -> None:
    owner_id = _create_user(client, "owner@example.com", "Owner")
    owner_headers = _headers(owner_id)

    agency_payload = {
        "name": "Acme Agency",
        "tier": "agency",
        "primary_client_name": "Client One",
    }
    agency_resp = client.post("/agencies", json=agency_payload, headers=owner_headers)
    assert agency_resp.status_code == 201, agency_resp.text
    agency_data = agency_resp.json()
    agency_id = agency_data["id"]
    primary_client_id = agency_data["default_client_id"]

    # create a second client (allowed for agency tier)
    client_payload = {"name": "Client Two"}
    client_resp = client.post(
        f"/agencies/{agency_id}/clients",
        json=client_payload,
        headers=owner_headers,
    )
    assert client_resp.status_code == 201, client_resp.text
    client_two_id = client_resp.json()["id"]

    # configure custom domain (pending until verified)
    domain_resp = client.post(
        f"/clients/{client_two_id}/domains",
        json={"domain": "client-two.example.com"},
        headers=owner_headers,
    )
    assert domain_resp.status_code == 201, domain_resp.text
    domain_data = domain_resp.json()
    assert domain_data["status"] == "pending"
    verification_token = domain_data["verification_token"]

    # attempt incorrect verification
    bad_verify = client.post(
        f"/domains/{domain_data['id']}/verify",
        json={"dns_record_value": "wrong-token"},
        headers=owner_headers,
    )
    assert bad_verify.status_code == 400

    # verify successfully using correct DNS token
    verify_resp = client.post(
        f"/domains/{domain_data['id']}/verify",
        json={"dns_record_value": verification_token},
        headers=owner_headers,
    )
    assert verify_resp.status_code == 200, verify_resp.text
    verified_data = verify_resp.json()
    assert verified_data["status"] == "active"
    assert verified_data["certificate_pem"].startswith("-----BEGIN CERTIFICATE-----")

    # configure branding defaults and client overrides
    agency_branding = {
        "company_name": "Acme",
        "logo_url": "https://cdn.example.com/acme.png",
        "primary_color": "#111111",
        "secondary_color": "#EEEEEE",
    }
    agency_brand_resp = client.put(
        f"/agencies/{agency_id}/branding",
        json=agency_branding,
        headers=owner_headers,
    )
    assert agency_brand_resp.status_code == 200

    client_branding = {
        "primary_color": "#FF0000",
        "logo_url": "https://cdn.example.com/client-two.png",
    }
    client_brand_resp = client.put(
        f"/clients/{client_two_id}/branding",
        json=client_branding,
        headers=owner_headers,
    )
    assert client_brand_resp.status_code == 200

    branding_lookup = client.get(f"/branding/by-domain/{'client-two.example.com'}")
    assert branding_lookup.status_code == 200
    branding = branding_lookup.json()
    assert branding["logo_url"] == "https://cdn.example.com/client-two.png"
    assert branding["primary_color"] == "#FF0000"
    assert branding["secondary_color"] == "#EEEEEE"
    assert branding["company_name"] == "Acme"

    # invitation flow
    invitation_resp = client.post(
        f"/agencies/{agency_id}/invitations",
        json={
            "email": "analyst@example.com",
            "role": "analyst",
            "client_id": client_two_id,
        },
        headers=owner_headers,
    )
    assert invitation_resp.status_code == 201, invitation_resp.text
    invitation_token = invitation_resp.json()["token"]

    analyst_id = _create_user(client, "analyst@example.com", "Analyst")
    analyst_headers = _headers(analyst_id)

    accept_resp = client.post(
        f"/invitations/{invitation_token}/accept",
        json={"email": "analyst@example.com"},
        headers=analyst_headers,
    )
    assert accept_resp.status_code == 200, accept_resp.text
    membership = accept_resp.json()
    assert membership["agency_id"] == agency_id
    assert membership["role"] == "analyst"
    assert membership["current_client_id"] == client_two_id

    # client switching for invited user
    switch_resp = client.post(
        f"/agencies/{agency_id}/switch-client",
        json={"client_id": primary_client_id},
        headers=analyst_headers,
    )
    assert switch_resp.status_code == 200, switch_resp.text
    switched_membership = switch_resp.json()
    assert switched_membership["current_client_id"] == primary_client_id

    context_resp = client.get(
        f"/agencies/{agency_id}/context",
        headers=analyst_headers,
    )
    assert context_resp.status_code == 200, context_resp.text
    context_data = context_resp.json()
    assert context_data["current_client_id"] == primary_client_id
    assert context_data["role"] == "analyst"


def test_agency_tier_gating(client: TestClient) -> None:
    owner_id = _create_user(client, "basic-owner@example.com", "Basic Owner")
    owner_headers = _headers(owner_id)

    agency_resp = client.post(
        "/agencies",
        json={"name": "Basic Agency", "tier": "basic"},
        headers=owner_headers,
    )
    assert agency_resp.status_code == 201
    agency_data = agency_resp.json()
    agency_id = agency_data["id"]
    client_id = agency_data["default_client_id"]

    # basic tier: cannot create additional clients
    second_client_resp = client.post(
        f"/agencies/{agency_id}/clients",
        json={"name": "Another Client"},
        headers=owner_headers,
    )
    assert second_client_resp.status_code == 403

    # basic tier: cannot configure custom domains
    domain_resp = client.post(
        f"/clients/{client_id}/domains",
        json={"domain": "basic-client.example.com"},
        headers=owner_headers,
    )
    assert domain_resp.status_code == 403

    # basic tier: cannot send invitations
    invitation_resp = client.post(
        f"/agencies/{agency_id}/invitations",
        json={"email": "new@example.com", "role": "manager"},
        headers=owner_headers,
    )
    assert invitation_resp.status_code == 403
