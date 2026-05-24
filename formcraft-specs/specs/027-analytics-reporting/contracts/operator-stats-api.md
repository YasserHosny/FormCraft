# API Contract: Operator Stats Widget

**Base path**: `/api/desk/my-stats`
**Auth**: Required (Bearer token)
**Role gate**: Any authenticated user (returns own data only)

---

## Endpoints

### GET /api/desk/my-stats

Lightweight stats for the current operator's Form Desk widget.

**Query params**: None (always returns current period stats).

**Response 200**:
```json
{
  "today": 12,
  "this_week": 58,
  "this_month": 234,
  "daily_trend": [
    {"date": "2026-05-18", "count": 8},
    {"date": "2026-05-19", "count": 11},
    {"date": "2026-05-20", "count": 9},
    {"date": "2026-05-21", "count": 14},
    {"date": "2026-05-22", "count": 7},
    {"date": "2026-05-23", "count": 9},
    {"date": "2026-05-24", "count": 12}
  ]
}
```

**Notes**:
- Always returns last 7 days of daily trend data
- Scoped to the authenticated user's own submissions only
- No role restrictions — all authenticated users can see their own stats
- Designed for quick rendering in a compact dashboard card

---

## Error Responses

| Status | When |
|--------|------|
| 401 | No valid auth token |
