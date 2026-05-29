import pytest
from uuid import uuid4
from postgrest.exceptions import APIError

from app.services.template_service import TemplateService


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeInsert:
    def __init__(self, client, table_name, payload):
        self.client = client
        self.table_name = table_name
        self.payload = payload

    def execute(self):
        return self.client.insert(self.table_name, self.payload)


class FakeTable:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name

    def insert(self, payload):
        return FakeInsert(self.client, self.table_name, payload)


class FakeClient:
    def __init__(self, missing_columns=None):
        self.missing_columns = missing_columns or {}
        self.inserts = {"templates": [], "pages": []}

    def table(self, table_name):
        return FakeTable(self, table_name)

    def insert(self, table_name, payload):
        for column in self.missing_columns.get(table_name, []):
            if column in payload:
                raise APIError(
                    {
                        "code": "PGRST204",
                        "message": f"Could not find the '{column}' column of '{table_name}' in the schema cache",
                        "details": None,
                        "hint": None,
                    }
                )
        row = dict(payload)
        self.inserts.setdefault(table_name, []).append(row)
        return FakeResponse([dict(row)])


async def fake_get_created_template(service, _template_id):
    template = dict(service.client.inserts["templates"][0])
    template["pages"] = [dict(service.client.inserts["pages"][0])]
    return template


@pytest.mark.asyncio
async def test_create_template_with_page_setup(monkeypatch):
    service = TemplateService(FakeClient())
    monkeypatch.setattr(service, "get_template", lambda template_id: fake_get_created_template(service, template_id))
    result = await service.create_template(
        data={
            "name": "Test Template",
            "description": "A test",
            "category": "KYC",
            "language": "AR",
            "country": "EG",
            "currency": "EGP",
            "tags": ["test"],
            "page_setup": {
                "page_size": "A4",
                "orientation": "landscape",
                "margins": {"top": 15, "bottom": 15, "left": 15, "right": 15},
            },
        },
        user_id=uuid4(),
        org_id=uuid4(),
    )
    assert result["name"] == "Test Template"
    assert result["currency"] == "EGP"
    pages = result.get("pages", [])
    assert len(pages) == 1
    page = pages[0]
    assert page["orientation"] == "landscape"
    assert page["margin_top_mm"] == 15
    assert page["width_mm"] == 297
    assert page["height_mm"] == 210


@pytest.mark.asyncio
async def test_create_template_custom_page_size(monkeypatch):
    service = TemplateService(FakeClient())
    monkeypatch.setattr(service, "get_template", lambda template_id: fake_get_created_template(service, template_id))
    result = await service.create_template(
        data={
            "name": "Custom Size",
            "page_setup": {
                "page_size": "Custom",
                "custom_width_mm": 300,
                "custom_height_mm": 400,
                "orientation": "portrait",
                "margins": {"top": 10, "bottom": 10, "left": 10, "right": 10},
            },
        },
        user_id=uuid4(),
        org_id=uuid4(),
    )
    pages = result.get("pages", [])
    assert pages[0]["width_mm"] == 300
    assert pages[0]["height_mm"] == 400


@pytest.mark.asyncio
async def test_create_template_retries_without_pending_migration_columns(monkeypatch):
    client = FakeClient(
        {
            "templates": ["currency", "tags"],
            "pages": ["orientation", "margin_top_mm"],
        }
    )
    service = TemplateService(client)
    monkeypatch.setattr(service, "get_template", lambda template_id: fake_get_created_template(service, template_id))

    result = await service.create_template(
        data={
            "name": "Legacy DB Compatible",
            "description": "",
            "category": "general",
            "language": "ar",
            "country": "EG",
            "currency": "EGP",
            "tags": ["legacy"],
            "page_setup": {
                "page_size": "A4",
                "orientation": "portrait",
                "margins": {"top": 10, "bottom": 10, "left": 10, "right": 10},
            },
        },
        user_id=uuid4(),
        org_id=uuid4(),
    )

    inserted_template = client.inserts["templates"][0]
    inserted_page = client.inserts["pages"][0]
    assert "currency" not in inserted_template
    assert "tags" not in inserted_template
    assert "orientation" not in inserted_page
    assert "margin_top_mm" not in inserted_page
    assert result["currency"] == "EGP"
    assert result["tags"] == ["legacy"]
    assert result["pages"][0]["orientation"] == "portrait"
    assert result["pages"][0]["margin_top_mm"] == 10


@pytest.mark.asyncio
async def test_preview_clone(mock_supabase_client):
    service = TemplateService(mock_supabase_client)
    source_id = uuid4()
    preview = await service.preview_clone(source_id, user_id=uuid4())
    assert preview["template_id"] == str(source_id)
    assert "page_count" in preview
    assert "element_count" in preview
