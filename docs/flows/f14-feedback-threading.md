# F14 — Feedback Threading & Replies

**Roles**: Admin (reply, view threads) · All authenticated users (view own, reply)  
**Related**: [F11 Feedback Widget](f11-feedback-widget.md) · [F12 Search & Labels](f12-feedback-labels.md)

---

## Thread panel wireframe (admin view)

```
┌──────────────────────────────────────────────────────────┐
│  [↑ Load earlier messages]                               │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Yasser Admin · مشرف            2026-05-11 10:22 │    │
│  │  شكراً على ملاحظتك، سنتابع هذا الأمر فوراً.    │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│     ┌──────────────────────────────────────────────┐     │
│     │  Ahmed User · مستخدم        2026-05-11 11:05 │     │
│     │  شكراً، هل يمكن توقع وقت للإصلاح؟           │     │
│     └──────────────────────────────────────────────┘     │
│                                                          │
│  ┌────────────────────────────────────┐  [إرسال →]  │    │
│  │  اكتب ردًا...               0/2000 │              │    │
│  └────────────────────────────────────┘              │    │
│                                                          │
│  الحالة:  [جديد ▼]                                      │
└──────────────────────────────────────────────────────────┘
```

---

## Notification flow (real-time)

```mermaid
sequenceDiagram
    participant Admin
    participant API as Backend API
    participant DB as Supabase DB
    participant RT as Supabase Realtime
    participant User

    Admin->>API: POST /api/admin/feedback/:id/replies
    API->>DB: INSERT feedback_replies
    API->>DB: INSERT feedback_notifications (recipient=User)
    API->>DB: UPDATE reply_count on submission
    DB-->>RT: broadcast row insert event
    RT-->>User: event received within ~5 s
    User->>User: notification badge increments

    User->>API: GET /api/my-feedback (open page)
    API->>DB: SELECT undelivered notifications → UPDATE delivered_at
    User->>API: expand thread → GET /api/feedback/:id/replies
    API-->>User: replies list
    User->>API: GET /api/notifications/:id/read
    API->>DB: UPDATE read_at
    User->>User: badge decrements
```

---

## Wireflow — Admin reply + unread indicator lifecycle

```mermaid
flowchart TD
    A([Admin opens /admin/feedback]) --> B[Clicks on submission row]
    B --> C[Thread panel expands]
    C --> D[GET /api/admin/feedback/:id/replies]
    D --> E[PATCH /api/admin/feedback/:id/read\nclear has_unread_user_reply]
    E --> F[Unread indicator removed from row]
    F --> G[Admin types reply in text box]
    G --> H{char count ≤ 2000?}
    H -- no --> I[Send button disabled]
    H -- yes --> J[Admin clicks إرسال]
    J --> K[POST /api/admin/feedback/:id/replies]
    K --> L[Reply appears in thread]
    K --> M[Notification row created for submission owner]
    M --> N[Realtime event sent to User within 5 s]
```

---

## Wireflow — Paginated thread load

```mermaid
flowchart LR
    A([Thread expanded — 20 replies shown]) --> B{has_earlier = true?}
    B -- no --> C[Load earlier button hidden]
    B -- yes --> D[Load earlier button visible]
    D --> E[User clicks Load earlier messages]
    E --> F["GET /api/feedback/:id/replies?limit=20&before_id={oldest_visible_id}"]
    F --> G[Older replies returned]
    G --> H[Prepend to top of thread list]
    H --> I[Scroll position preserved]
    I --> B
```

---

## Flows

### 14.1 Admin replies to a feedback submission

```
Admin opens /admin/feedback → clicks on a submission row
→ Thread panel expands inline below the row
→ Shows original submission text (and media if any)
→ Shows all existing replies in chronological order
→ Admin types reply in text box (max 2000 chars, counter shown)
→ Clicks "إرسال"
→ POST /api/admin/feedback/{id}/replies with { text_content }
→ Reply appears in thread immediately with author + timestamp
→ User receives in-app notification within 5 seconds (Supabase Realtime)
```

### 14.2 Admin changes submission status from thread panel

```
Thread panel shows "الحالة:" dropdown at bottom
→ Admin selects: جديد / تمت المراجعة / تم الحل
→ PATCH /api/admin/feedback/{id}/status called
→ Status badge in table row updates immediately (no reload)
```

### 14.3 User views "My Feedback" page

```
Authenticated user navigates to /my-feedback
→ GET /api/my-feedback called
→ Page lists all user's own submissions ordered by most recent
→ Each card shows: page URL, date, status badge, reply count badge
→ User clicks a card to expand it
→ GET /api/feedback/{id}/replies called → replies loaded
→ Replies in chronological order:
    Admin replies: highlighted card (blue background), "مشرف" badge
    User replies: plain card, right-aligned
→ Most recent 20 replies shown; "Load earlier messages" for older ones
```

### 14.4 User replies to admin

```
User is on /my-feedback, thread expanded
→ Types message in reply box (max 2000 chars)
→ Clicks "إرسال"
→ POST /api/feedback/{id}/replies with { text_content }
→ Reply appears at bottom of thread
→ Admin dashboard shows unread indicator on that submission
→ Indicator auto-cleared when admin expands the thread
```

### 14.5 In-app notification flow

```
Event: Admin posts reply to submission owned by User A
→ Backend creates FeedbackNotification row:
    recipient_user_id = User A, feedback_id, reply_id, created_at
→ Supabase Realtime broadcasts row insert to User A's live channel
→ Frontend receives event within ~5 seconds
→ Notification badge in nav header increments
→ User A opens /my-feedback → notification marked delivered
→ User A expands thread → read_at set → badge decrements

Event: User A posts reply
→ Admin dashboard submission row shows unread indicator (has_unread_user_reply = true)
→ Indicator cleared when admin expands that thread
```

### 14.6 Notification persistence (offline user)

```
User A is offline when admin posts reply
→ Notification row persists in DB (delivered_at = null)
→ On next login, GET /api/notifications returns undelivered notifications
→ Badge shows correct unread count
→ User sees reply on /my-feedback when they open it
```

### 14.7 Pagination of long threads

```
Thread has > 20 replies
→ Most recent 20 loaded on expand
→ "Load earlier messages" button appears at top of thread list
→ User clicks → GET /api/feedback/{id}/replies?limit=20&before_id={oldest_visible_id}
→ Older replies prepended above current list
→ Scroll position remains anchored to current view
→ Button hidden when no more replies remain (has_earlier = false)
```
