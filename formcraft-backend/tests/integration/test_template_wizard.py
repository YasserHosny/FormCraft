import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.skip(reason="Requires auth and DB setup")
def test_create_template_with_wizard_fields():
    payload = {
        "name": "Integration Test",
        "category": "KYC",
        "language": "AR",
        "country": "EG",
        "currency": "SAR",
        "tags": ["integration"],
        "page_setup": {
            "page_size": "A4",
            "orientation": "portrait",
            "margins": {"top": 10, "bottom": 10, "left": 10, "right": 10},
        },
    }
    response = client.post("/api/templates", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["currency"] == "SAR"
    assert data["tags"] == ["integration"]
    assert len(data["pages"]) == 1
    page = data["pages"][0]
    assert page["orientation"] == "portrait"
    assert page["margin_top_mm"] == 10


@pytest.mark.skip(reason="Requires auth and DB setup")
def test_clone_preview_endpoint():
    response = client.post("/api/templates/123e4567-e89b-12d3-a456-426614174000/clone?preview=true", json={})
    assert response.status_code in (200, 404)


@pytest.mark.skip(reason="Requires auth and DB setup")
def test_org_categories_endpoint():
    response = client.get("/api/org-categories")
    assert response.status_code in (200, 401, 422)
