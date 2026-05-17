"""Service for printer profile CRUD and calibration page generation."""

from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.models.print_settings import PrinterProfile


class PrinterProfileService:
    def __init__(self, client: Client):
        self.client = client

    async def create_profile(self, data: dict, org_id: UUID, user_id: UUID) -> PrinterProfile:
        if data.get("is_default"):
            await self._unset_current_default(org_id)

        payload = {
            **data,
            "org_id": str(org_id),
            "created_by": str(user_id),
        }
        result = self.client.table("printer_profiles").insert(payload).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create printer profile")
        return PrinterProfile(**result.data[0])

    async def list_profiles(self, include_inactive: bool = False) -> list[dict]:
        query = self.client.table("printer_profiles").select("*").order("name")
        if not include_inactive:
            query = query.eq("is_active", True)
        result = query.execute()
        return result.data or []

    async def update_profile(self, profile_id: UUID, data: dict) -> dict:
        result = (
            self.client.table("printer_profiles")
            .update({**data, "updated_at": "now()"})
            .eq("id", str(profile_id))
            .eq("is_active", True)
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Printer profile not found")
        return result.data[0]

    async def delete_profile(self, profile_id: UUID) -> dict:
        result = (
            self.client.table("printer_profiles")
            .update({"is_active": False, "is_default": False, "updated_at": "now()"})
            .eq("id", str(profile_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Printer profile not found")
        return result.data[0]

    async def set_default(self, profile_id: UUID, org_id: UUID) -> dict:
        await self._unset_current_default(org_id)
        result = (
            self.client.table("printer_profiles")
            .update({"is_default": True, "updated_at": "now()"})
            .eq("id", str(profile_id))
            .eq("is_active", True)
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Printer profile not found")
        return result.data[0]

    async def get_default_profile(self, org_id: UUID) -> dict | None:
        result = (
            self.client.table("printer_profiles")
            .select("*")
            .eq("is_default", True)
            .eq("is_active", True)
            .single()
            .execute()
        )
        return result.data if result.data else None

    def generate_calibration_page(self, x_offset_mm: float, y_offset_mm: float) -> str:
        markers = []
        positions = [(20, 20), (100, 20), (20, 140), (100, 140), (60, 80)]
        for x, y in positions:
            ax = x + x_offset_mm
            ay = y + y_offset_mm
            markers.append(
                f'<div style="position:absolute;left:{ax}mm;top:{ay}mm;'
                f'width:10mm;height:10mm;border:0.2mm solid black;">'
                f'<div style="position:absolute;left:4.9mm;top:0;width:0.2mm;height:10mm;background:black;"></div>'
                f'<div style="position:absolute;top:4.9mm;left:0;width:10mm;height:0.2mm;background:black;"></div>'
                f'<span style="position:absolute;bottom:-4mm;left:0;font-size:6pt;">({x},{y})</span>'
                f'</div>'
            )

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@page {{ size: A4; margin: 0; }}
body {{ margin: 0; font-family: sans-serif; }}
.page {{ position: relative; width: 210mm; height: 297mm; }}
.title {{ position: absolute; top: 5mm; left: 50%; transform: translateX(-50%); font-size: 10pt; }}
.offset-info {{ position: absolute; bottom: 10mm; left: 10mm; font-size: 8pt; color: #666; }}
</style></head>
<body><div class="page">
<div class="title">Calibration Page — Offset: X={x_offset_mm}mm, Y={y_offset_mm}mm</div>
{''.join(markers)}
<div class="offset-info">Expected crosshair centers: (20,20), (100,20), (20,140), (100,140), (60,80) mm from top-left</div>
</div></body></html>"""
        return html

    async def _unset_current_default(self, org_id: UUID) -> None:
        self.client.table("printer_profiles").update(
            {"is_default": False, "updated_at": "now()"}
        ).eq("is_default", True).eq("is_active", True).execute()
