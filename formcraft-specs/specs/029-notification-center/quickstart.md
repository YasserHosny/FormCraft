# Quickstart: Notification Center

**Feature**: 029-notification-center
**Date**: 2026-05-25

---

## Prerequisites

- FormCraft backend running (`formcraft-backend/`)
- FormCraft frontend running (`formcraft-frontend/`)
- Supabase instance with existing migrations applied (001–030)
- Migration 031 (notification_center) applied
- At least one organization with departments, designers, branch_managers, and operators
- SMTP credentials configured in environment variables (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`)
- Approval workflow enabled (F28) for template transition event testing

---

## Test Scenarios

### Scenario 1: In-App Notification on Template Approval (P1 — Core)

**Setup**: Org with approval_workflow_enabled=true, 1 Designer, 1 Branch Manager, 1 Admin.

1. Log in as Designer -> create a template -> submit for review
2. Log in as Branch Manager -> approve the template
3. **Without refreshing**, observe the Designer's nav bar within 30 seconds
4. Verify: Bell icon shows unread badge (count >= 1)
5. Click the bell icon -> verify dropdown opens
6. Verify: Notification shows "Template approved" with template name
7. Verify: Notification shows bilingual title (Arabic + English based on user language)
8. Verify: Timestamp shows relative time ("just now" or "seconds ago")
9. Click the notification -> verify navigation to the template in designer
10. Verify: Notification is now marked as read (styling changes)
11. Verify: Bell badge count decrements by 1

**Expected**: Full in-app notification lifecycle works for template approval event.

### Scenario 2: Multiple Notification Types (P1 — Core)

**Setup**: Same as Scenario 1.

1. Designer submits template -> verify Branch Manager gets "Template submitted for review" notification
2. Branch Manager rejects template -> verify Designer gets "Template rejected" notification with comment
3. Designer edits and resubmits -> verify Branch Manager gets new submission notification
4. Branch Manager approves -> verify Designer and Admin get "Template approved" notification
5. Admin publishes -> verify all operators in department get "Template published" notification

**Expected**: Each template transition generates correct notification to correct recipients.

### Scenario 3: Mark All as Read (P1)

**Setup**: User with 5+ unread notifications.

1. Verify bell badge shows unread count (e.g., "5")
2. Click bell -> verify dropdown shows 5 unread notifications (bold/highlighted styling)
3. Click "Mark all as read"
4. Verify: Badge count resets to 0
5. Verify: All notifications in dropdown show read styling
6. Close and reopen dropdown -> verify state persists

**Expected**: Mark all as read updates all notifications and badge in one action.

### Scenario 4: Notification Preferences — Disable Email (P2)

**Setup**: User with default preferences (all enabled).

1. Navigate to profile -> notification preferences
2. Verify: Table shows all 9 notification types with in-app and email toggles
3. Disable email for "Template published"
4. Trigger a template publish event
5. Verify: User receives in-app notification (bell badge updates)
6. Verify: No email is sent for "Template published"
7. Trigger a template approval event (email still enabled)
8. Verify: Both in-app notification AND email are received for "Template approved"

**Expected**: Per-type email toggle works independently. Disabling one type doesn't affect others.

### Scenario 5: Notification Preferences — Disable Both Channels (P2)

1. Navigate to notification preferences
2. Disable both in-app and email for "Template withdrawn"
3. Trigger a template withdrawal event
4. Verify: No notification appears in bell dropdown
5. Verify: No email sent
6. Verify: No notification row exists for this user in database

**Expected**: Disabling both channels suppresses notification creation entirely.

### Scenario 6: Email Delivery with Org Branding (P2)

**Setup**: Org with logo URL and primary color configured in org settings.

1. Enable email for "Template rejected" in preferences
2. Trigger a template rejection with a review comment
3. Check the recipient's email inbox
4. Verify email contains:
   - Org logo in header
   - Org primary color in header bar
   - Bilingual title (Arabic and English)
   - Reviewer's name and comment
   - "View Template" button linking to the template
   - Unsubscribe link in footer
5. Click the "View Template" button -> verify it navigates to the template page
6. Click the unsubscribe link -> verify confirmation page
7. Verify: Email channel is now disabled for "Template rejected" in preferences

**Expected**: HTML email renders with org branding, bilingual content, action link, and working unsubscribe.

### Scenario 7: Full Notification History Page (P3)

**Setup**: User with 50+ notifications of mixed types over the past 30 days.

1. Navigate to `/notifications`
2. Verify: Paginated list of all notifications (20 per page)
3. Verify each notification shows: type icon, title, body preview, timestamp, read/unread styling
4. Filter by type "Template approval" -> verify only approval notifications shown
5. Filter by status "Unread" -> verify only unread notifications shown
6. Filter by date range (last 7 days) -> verify correct time filtering
7. Click a notification -> verify navigation to linked page
8. Navigate back -> verify read state persists

**Expected**: Full history with working filters, pagination, and navigation.

### Scenario 8: System Announcements (P3)

**Setup**: 1 Admin, multiple users across roles and departments.

1. Log in as Admin -> navigate to admin announcements page
2. Create announcement: title (AR + EN), body, target "All users"
3. Click "Send"
4. Verify: Success message with recipient count
5. Log in as Designer -> verify announcement appears in bell dropdown
6. Verify: Announcement has megaphone icon and is pinned at top (above regular notifications)
7. Log in as Operator -> verify same announcement visible
8. Create another announcement targeting "Retail Banking" department operators only
9. Log in as Retail Banking operator -> verify announcement visible
10. Log in as different department operator -> verify announcement NOT visible

**Expected**: Announcements reach targeted audience with distinct styling and pinned positioning.

---

## API Smoke Tests

### Unread Count
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/notifications/unread-count"
# Expected: {"unread_count": N}
```

### List Notifications
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/notifications?page=1&page_size=5"
# Expected: {"notifications": [...], "total": N, "page": 1, "page_size": 5}
```

### List with Filters
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/notifications?type=template_approved&status=unread"
# Expected: Only unread template_approved notifications
```

### Mark Single as Read
```bash
curl -X PATCH -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/notifications/$NOTIFICATION_ID/read"
# Expected: {"id": "...", "read_at": "2026-05-25T..."}
```

### Mark All as Read
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/notifications/read-all"
# Expected: {"marked_count": N}
```

### Get Preferences
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/notifications/preferences"
# Expected: {"preferences": [{...}, ...]} with 9 notification types
```

### Update Preferences
```bash
curl -X PATCH -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"preferences": [{"notification_type": "template_approved", "in_app_enabled": true, "email_enabled": false}]}' \
  "$API_URL/api/notifications/preferences"
# Expected: {"updated": 1}
```

### Create Announcement (Admin only)
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title_ar": "اختبار", "title_en": "Test", "body_ar": "محتوى", "body_en": "Content", "target_audience": "all"}' \
  "$API_URL/api/admin/announcements"
# Expected: {"announcement_id": "...", "recipients_count": N, "created_at": "..."}
```
