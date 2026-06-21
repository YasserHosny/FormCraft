"""Notification engine: create, route, query, and manage notifications."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.models.enums import EmailStatus, NotificationType


class NotificationService:
    def __init__(self, client: Client):
        self.client = client

    # --- Content helpers ---

    def build_notification_content(
        self,
        event_type: NotificationType,
        template_name: str,
        actor_name: str,
        comment: str | None = None,
    ) -> dict:
        """Return bilingual title/body for each event type."""
        content_map = {
            NotificationType.TEMPLATE_SUBMITTED_FOR_REVIEW: {
                "title_ar": f"تم تقديم قالب '{template_name}' للمراجعة",
                "title_en": f"Template '{template_name}' submitted for review",
                "body_ar": f"قام {actor_name} بتقديم قالب جديد للمراجعة.",
                "body_en": f"{actor_name} submitted a new template for review.",
            },
            NotificationType.TEMPLATE_APPROVED: {
                "title_ar": f"تمت الموافقة على قالب '{template_name}'",
                "title_en": f"Template '{template_name}' approved",
                "body_ar": f"قام {actor_name} بالموافقة على القالب.",
                "body_en": f"{actor_name} approved the template.",
            },
            NotificationType.TEMPLATE_REJECTED: {
                "title_ar": f"تم رفض قالب '{template_name}'",
                "title_en": f"Template '{template_name}' rejected",
                "body_ar": f"قام {actor_name} برفض القالب. السبب: {comment or 'لا يوجد تعليق'}",
                "body_en": f"{actor_name} rejected the template. Reason: {comment or 'No comment'}",
            },
            NotificationType.TEMPLATE_PUBLISHED: {
                "title_ar": f"تم نشر قالب '{template_name}'",
                "title_en": f"Template '{template_name}' published",
                "body_ar": "القالب متاح الآن في مكتبة النماذج.",
                "body_en": "The template is now available in the template library.",
            },
            NotificationType.TEMPLATE_WITHDRAWN: {
                "title_ar": f"تم سحب قالب '{template_name}'",
                "title_en": f"Template '{template_name}' withdrawn",
                "body_ar": "قام المصمم بسحب القالب من المراجعة.",
                "body_en": "Designer withdrew the template from review.",
            },
            NotificationType.TEMPLATE_FEEDBACK_RECEIVED: {
                "title_ar": "تم استلام تعليق جديد",
                "title_en": "New feedback received",
                "body_ar": f"تعليق من {actor_name} على القالب.",
                "body_en": f"Feedback from {actor_name} on the template.",
            },
            NotificationType.TEMPLATE_FEEDBACK_RESOLVED: {
                "title_ar": "تم حل التعليق",
                "title_en": "Feedback resolved",
                "body_ar": f"تم حل التعليق بواسطة {actor_name}.",
                "body_en": f"Feedback resolved by {actor_name}.",
            },
            NotificationType.DRAFT_EXPIRING: {
                "title_ar": f"مسودة '{template_name}' على وشك الانتهاء",
                "title_en": f"Draft '{template_name}' expiring soon",
                "body_ar": "لم يتم تعديل المسودة منذ 30 يومًا.",
                "body_en": "Draft hasn't been modified in 30 days.",
            },
            NotificationType.SYSTEM_ANNOUNCEMENT: {
                "title_ar": "إعلان نظام",
                "title_en": "System Announcement",
                "body_ar": "",
                "body_en": "",
            },
            NotificationType.SUBSCRIPTION_PAYMENT_FAILED: {
                "title_ar": "فشل تجديد الاشتراك",
                "title_en": "Subscription Renewal Failed",
                "body_ar": "فشل تجديد اشتراكك. يرجى تحديث طريقة الدفع للحفاظ على خدماتك.",
                "body_en": "Your subscription renewal payment failed. Please update your payment method to keep your services active.",
            },
        }
        return content_map.get(
            event_type,
            {
                "title_ar": "إشعار جديد",
                "title_en": "New Notification",
                "body_ar": "",
                "body_en": "",
            },
        )

    # --- Core methods ---

    async def create_notifications(
        self,
        org_id: UUID,
        recipient_ids: list[UUID],
        notification_type: NotificationType,
        title_ar: str,
        title_en: str,
        body_ar: str | None = None,
        body_en: str | None = None,
        action_url: str | None = None,
        source_id: UUID | None = None,
        source_type: str | None = None,
        is_announcement: bool = False,
        created_by: UUID | None = None,
    ) -> list[dict]:
        """Batch-create notifications for multiple recipients, respecting preferences."""
        if not recipient_ids:
            return []

        # Load org default preferences
        org_defaults = await self._get_org_notification_defaults(org_id)
        type_defaults = org_defaults.get(
            notification_type.value, {"in_app": True, "email": True}
        )

        notifications = []
        for recipient_id in recipient_ids:
            # Check user preference override
            user_pref = await self._get_user_preference(
                org_id, recipient_id, notification_type
            )
            in_app_enabled = user_pref.get(
                "in_app_enabled", type_defaults.get("in_app", True)
            )
            email_enabled = user_pref.get(
                "email_enabled", type_defaults.get("email", True)
            )

            if not in_app_enabled and not email_enabled:
                continue  # Skip entirely

            email_status = EmailStatus.PENDING if email_enabled else EmailStatus.SKIPPED

            notifications.append(
                {
                    "recipient_id": str(recipient_id),
                    "org_id": str(org_id),
                    "type": notification_type.value,
                    "title_ar": title_ar,
                    "title_en": title_en,
                    "body_ar": body_ar,
                    "body_en": body_en,
                    "action_url": action_url,
                    "source_id": str(source_id) if source_id else None,
                    "source_type": source_type,
                    "is_announcement": is_announcement,
                    "email_status": email_status.value,
                    "created_by": str(created_by) if created_by else None,
                }
            )

        if not notifications:
            return []

        # Batch insert in chunks of 100
        inserted = []
        for chunk in [
            notifications[i : i + 100] for i in range(0, len(notifications), 100)
        ]:
            result = self.client.table("notifications").insert(chunk).execute()
            if result.data:
                inserted.extend(result.data)

        return inserted

    async def get_notifications(
        self,
        user_id: UUID,
        org_id: UUID,
        page: int = 1,
        page_size: int = 20,
        type_filter: str | None = None,
        read_status: str | None = None,  # 'read', 'unread', 'all'
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[dict], int]:
        """Query notifications for a user with filters."""
        query = (
            self.client.table("notifications")
            .select("*", count="exact")
            .eq("recipient_id", str(user_id))
            .eq("org_id", str(org_id))
            .order("is_announcement", desc=True)
            .order("created_at", desc=True)
        )

        if type_filter:
            query = query.eq("type", type_filter)
        if read_status == "read":
            query = query.not_.is_("read_at", "null")
        elif read_status == "unread":
            query = query.is_("read_at", "null")
        if date_from:
            query = query.gte("created_at", date_from)
        if date_to:
            query = query.lte("created_at", date_to)

        start = (page - 1) * page_size
        result = query.range(start, start + page_size - 1).execute()

        return result.data or [], result.count or 0

    async def get_unread_count(self, user_id: UUID, org_id: UUID) -> int:
        result = (
            self.client.table("notifications")
            .select("id", count="exact")
            .eq("recipient_id", str(user_id))
            .eq("org_id", str(org_id))
            .is_("read_at", "null")
            .execute()
        )
        return result.count or 0

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> dict:
        result = (
            self.client.table("notifications")
            .update({"read_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", str(notification_id))
            .eq("recipient_id", str(user_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
        return result.data[0]

    async def mark_all_as_read(self, user_id: UUID, org_id: UUID) -> int:
        result = (
            self.client.table("notifications")
            .update({"read_at": datetime.now(timezone.utc).isoformat()})
            .eq("recipient_id", str(user_id))
            .eq("org_id", str(org_id))
            .is_("read_at", "null")
            .execute()
        )
        return len(result.data or [])

    async def get_preferences(self, user_id: UUID, org_id: UUID) -> list[dict]:
        """Return merged preferences: user overrides + org defaults with is_default flag."""
        org_defaults = await self._get_org_notification_defaults(org_id)

        # Get user overrides
        user_prefs_result = (
            self.client.table("notification_preferences")
            .select("*")
            .eq("user_id", str(user_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        user_prefs = {p["notification_type"]: p for p in (user_prefs_result.data or [])}

        preferences = []
        for ntype in NotificationType:
            defaults = org_defaults.get(ntype.value, {"in_app": True, "email": True})
            user_pref = user_prefs.get(ntype.value)

            if user_pref:
                preferences.append(
                    {
                        "notification_type": ntype.value,
                        "in_app_enabled": user_pref["in_app_enabled"],
                        "email_enabled": user_pref["email_enabled"],
                        "is_default": False,
                    }
                )
            else:
                preferences.append(
                    {
                        "notification_type": ntype.value,
                        "in_app_enabled": defaults.get("in_app", True),
                        "email_enabled": defaults.get("email", True),
                        "is_default": True,
                    }
                )

        return preferences

    async def update_preference(
        self,
        user_id: UUID,
        org_id: UUID,
        notification_type: str,
        in_app: bool,
        email: bool,
    ) -> dict:
        data = {
            "user_id": str(user_id),
            "org_id": str(org_id),
            "notification_type": notification_type,
            "in_app_enabled": in_app,
            "email_enabled": email,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        result = self.client.table("notification_preferences").upsert(data).execute()
        return result.data[0] if result.data else {}

    # --- Internal helpers ---

    async def _get_org_notification_defaults(self, org_id: UUID) -> dict:
        try:
            result = (
                self.client.table("organizations")
                .select("settings")
                .eq("id", str(org_id))
                .single()
                .execute()
            )
            if result.data and result.data.get("settings"):
                prefs = result.data["settings"].get("notification_preferences", {})
                return prefs.get("defaults", {})
        except Exception:
            pass
        return {}

    async def _get_user_preference(
        self, org_id: UUID, user_id: UUID, notification_type: NotificationType
    ) -> dict:
        try:
            result = (
                self.client.table("notification_preferences")
                .select("*")
                .eq("user_id", str(user_id))
                .eq("org_id", str(org_id))
                .eq("notification_type", notification_type.value)
                .single()
                .execute()
            )
            if result.data:
                return {
                    "in_app_enabled": result.data.get("in_app_enabled", True),
                    "email_enabled": result.data.get("email_enabled", True),
                }
        except Exception:
            pass
        return {}
