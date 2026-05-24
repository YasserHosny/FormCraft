"""Review queue query, metrics, timeline, and export services."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client


class ReviewQueueService:
    def __init__(self, client: Client):
        self.client = client

    async def get_review_queue(
        self,
        org_id: UUID,
        status_filter: str | None = None,
        department_id: UUID | None = None,
        designer_id: UUID | None = None,
        sort_by: str = "submitted_at",
        sort_dir: str = "asc",
    ) -> dict:
        """Query pending/approved/rejected templates with designer and department info."""
        query = (
            self.client.table("templates")
            .select(
                "id, name, category, status, version, created_by, department_id, updated_at, "
                "profiles!templates_created_by_fkey(display_name), "
                "departments!templates_department_id_fkey(name_en)"
            )
            .eq("org_id", str(org_id))
            .in_(
                "status",
                ["submitted_for_review", "approved", "rejected"]
                if not status_filter
                else [status_filter],
            )
        )

        if department_id:
            query = query.eq("department_id", str(department_id))
        if designer_id:
            query = query.eq("created_by", str(designer_id))

        # Get org settings for overdue threshold
        threshold_days = await self._get_overdue_threshold(org_id)

        result = query.execute()
        items = []
        overdue_count = 0
        now = datetime.now(timezone.utc)

        for t in result.data or []:
            submitted_at = datetime.fromisoformat(
                t["updated_at"].replace("Z", "+00:00")
            )
            days_waiting = (now - submitted_at).days
            is_overdue = (
                days_waiting > threshold_days and t["status"] == "submitted_for_review"
            )
            if is_overdue:
                overdue_count += 1

            profile = t.get("profiles") or {}
            dept = t.get("departments") or {}

            items.append(
                {
                    "template_id": t["id"],
                    "template_name": t["name"],
                    "category": t.get("category", "general"),
                    "status": t["status"],
                    "version": t.get("version", 1),
                    "designer_id": t["created_by"],
                    "designer_name": profile.get("display_name")
                    if isinstance(profile, dict)
                    else None,
                    "department_name": dept.get("name_en")
                    if isinstance(dept, dict)
                    else None,
                    "submitted_at": submitted_at.isoformat(),
                    "days_waiting": days_waiting,
                    "is_overdue": is_overdue,
                }
            )

        # Sort
        reverse = sort_dir.lower() == "desc"
        if sort_by == "days_waiting":
            items.sort(key=lambda x: x["days_waiting"], reverse=reverse)
        elif sort_by == "name":
            items.sort(key=lambda x: x["template_name"], reverse=reverse)
        else:
            items.sort(key=lambda x: x["submitted_at"], reverse=reverse)

        return {"items": items, "total": len(items), "overdue_count": overdue_count}

    async def get_governance_metrics(
        self, org_id: UUID, since: datetime | None = None
    ) -> dict:
        """Compute governance metrics from template_reviews and templates."""
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(days=30)

        since_str = since.isoformat()

        # Pending count
        pending_result = (
            self.client.table("templates")
            .select("id", count="exact")
            .eq("org_id", str(org_id))
            .eq("status", "submitted_for_review")
            .execute()
        )
        pending_count = pending_result.count or 0

        # Approved awaiting publish
        approved_result = (
            self.client.table("templates")
            .select("id", count="exact")
            .eq("org_id", str(org_id))
            .eq("status", "approved")
            .execute()
        )
        approved_awaiting_publish = approved_result.count or 0

        # Reviews stats
        reviews_result = (
            self.client.table("template_reviews")
            .select("action, created_at")
            .eq("org_id", str(org_id))
            .gte("created_at", since_str)
            .execute()
        )
        reviews = reviews_result.data or []
        total_reviews = len(reviews)
        rejected_count = sum(1 for r in reviews if r["action"] == "rejected")
        rejection_rate_pct = (
            round(100.0 * rejected_count / total_reviews, 1) if total_reviews else 0.0
        )

        # Overdue count
        threshold_days = await self._get_overdue_threshold(org_id)
        overdue_templates = (
            self.client.table("templates")
            .select("id")
            .eq("org_id", str(org_id))
            .eq("status", "submitted_for_review")
            .lt(
                "updated_at",
                (
                    datetime.now(timezone.utc) - timedelta(days=threshold_days)
                ).isoformat(),
            )
            .execute()
        )
        overdue_count = len(overdue_templates.data or [])

        # Average turnaround (approximate: review.created_at - template.updated_at when submitted)
        # This is a simplified calculation
        avg_turnaround_days = None
        if total_reviews > 0:
            # We can't easily compute exact turnaround without knowing when each template was submitted,
            # so we use a heuristic: for approved templates, avg days between submission and approval
            approved_reviews = [r for r in reviews if r["action"] == "approved"]
            if approved_reviews:
                # Get template updated_at for each review
                turnaround_sum = 0
                count = 0
                for r in approved_reviews:
                    tmpl = (
                        self.client.table("templates")
                        .select("updated_at")
                        .eq("id", r.get("template_id"))
                        .execute()
                    )
                    if tmpl.data:
                        submitted = datetime.fromisoformat(
                            tmpl.data[0]["updated_at"].replace("Z", "+00:00")
                        )
                        reviewed = datetime.fromisoformat(
                            r["created_at"].replace("Z", "+00:00")
                        )
                        turnaround_sum += (reviewed - submitted).total_seconds() / 86400
                        count += 1
                avg_turnaround_days = (
                    round(turnaround_sum / count, 1) if count else None
                )

        return {
            "pending_count": pending_count,
            "approved_awaiting_publish": approved_awaiting_publish,
            "avg_turnaround_days": avg_turnaround_days,
            "rejection_rate_pct": rejection_rate_pct,
            "overdue_count": overdue_count,
            "total_reviews": total_reviews,
            "overdue_threshold_days": threshold_days,
        }

    async def get_timeline(self, org_id: UUID, template_id: UUID) -> dict:
        """Build chronological timeline of all review events for a template."""
        # Verify template belongs to org
        tmpl = (
            self.client.table("templates")
            .select("name, org_id")
            .eq("id", str(template_id))
            .single()
            .execute()
        )
        if not tmpl.data or tmpl.data.get("org_id") != str(org_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")

        # Get reviews
        reviews_result = (
            self.client.table("template_reviews")
            .select("*, profiles!template_reviews_reviewer_id_fkey(display_name, role)")
            .eq("template_id", str(template_id))
            .order("created_at", desc=False)
            .execute()
        )

        timeline = []
        for r in reviews_result.data or []:
            profile = r.get("profiles") or {}
            timeline.append(
                {
                    "event": r["action"],
                    "actor_id": r["reviewer_id"],
                    "actor_name": profile.get("display_name")
                    if isinstance(profile, dict)
                    else None,
                    "actor_role": profile.get("role")
                    if isinstance(profile, dict)
                    else None,
                    "timestamp": r["created_at"],
                    "comment": r.get("comment"),
                    "element_comments": r.get("element_comments"),
                }
            )

        # Add audit log events (submitted_for_review, published, withdrawn)
        audit_result = (
            self.client.table("audit_logs")
            .select("action, user_id, created_at, metadata")
            .eq("resource_id", str(template_id))
            .in_(
                "action",
                [
                    "TEMPLATE_SUBMITTED_FOR_REVIEW",
                    "TEMPLATE_PUBLISHED",
                    "TEMPLATE_WITHDRAWN",
                ],
            )
            .order("created_at", desc=False)
            .execute()
        )

        for a in audit_result.data or []:
            # Get actor name
            actor = (
                self.client.table("profiles")
                .select("display_name, role")
                .eq("id", a["user_id"])
                .single()
                .execute()
            )
            actor_name = actor.data.get("display_name") if actor.data else None
            actor_role = actor.data.get("role") if actor.data else None

            event_map = {
                "TEMPLATE_SUBMITTED_FOR_REVIEW": "submitted_for_review",
                "TEMPLATE_PUBLISHED": "published",
                "TEMPLATE_WITHDRAWN": "withdrawn",
            }

            timeline.append(
                {
                    "event": event_map.get(a["action"], a["action"]),
                    "actor_id": a["user_id"],
                    "actor_name": actor_name,
                    "actor_role": actor_role,
                    "timestamp": a["created_at"],
                    "comment": a.get("metadata", {}).get("comment")
                    if a.get("metadata")
                    else None,
                    "element_comments": None,
                }
            )

        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])

        return {
            "template_id": str(template_id),
            "template_name": tmpl.data.get("name", ""),
            "timeline": timeline,
        }

    async def get_default_reviewer(
        self, org_id: UUID, department_id: UUID
    ) -> dict | None:
        result = (
            self.client.table("department_default_reviewers")
            .select(
                "*, profiles!department_default_reviewers_reviewer_id_fkey(display_name)"
            )
            .eq("org_id", str(org_id))
            .eq("department_id", str(department_id))
            .single()
            .execute()
        )
        if not result.data:
            return None
        profile = result.data.get("profiles") or {}
        return {
            "department_id": str(department_id),
            "reviewer_id": result.data["reviewer_id"],
            "reviewer_name": profile.get("display_name")
            if isinstance(profile, dict)
            else None,
        }

    async def set_default_reviewer(
        self, org_id: UUID, department_id: UUID, reviewer_id: UUID
    ) -> dict:
        # Upsert
        data = {
            "org_id": str(org_id),
            "department_id": str(department_id),
            "reviewer_id": str(reviewer_id),
        }
        result = (
            self.client.table("department_default_reviewers").upsert(data).execute()
        )
        return await self.get_default_reviewer(org_id, department_id)

    async def remove_default_reviewer(self, org_id: UUID, department_id: UUID) -> None:
        self.client.table("department_default_reviewers").delete().eq(
            "org_id", str(org_id)
        ).eq("department_id", str(department_id)).execute()

    async def _get_overdue_threshold(self, org_id: UUID) -> int:
        try:
            result = (
                self.client.table("organizations")
                .select("settings")
                .eq("id", str(org_id))
                .single()
                .execute()
            )
            if result.data and result.data.get("settings"):
                return result.data["settings"].get("review_overdue_threshold_days", 3)
        except Exception:
            pass
        return 3
