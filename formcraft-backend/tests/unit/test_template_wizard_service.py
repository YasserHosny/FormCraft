import pytest
from uuid import uuid4

from app.services.template_service import TemplateService


@pytest.mark.asyncio
async def test_create_template_with_page_setup(mock_supabase_client):
    service = TemplateService(mock_supabase_client)
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
async def test_create_template_custom_page_size(mock_supabase_client):
    service = TemplateService(mock_supabase_client)
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
async def test_preview_clone(mock_supabase_client):
    service = TemplateService(mock_supabase_client)
    source_id = uuid4()
    preview = await service.preview_clone(source_id, user_id=uuid4())
    assert preview["template_id"] == str(source_id)
    assert "page_count" in preview
    assert "element_count" in preview
