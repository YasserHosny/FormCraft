# FormCraft Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-05-07

## Active Technologies

- Python 3.12 (backend), TypeScript / Angular 17 (frontend) + FastAPI, Supabase (PostgreSQL + Storage + Auth), Angular Material (001-customer-feedback)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.12 (backend), TypeScript / Angular 17 (frontend): Follow standard conventions

## Recent Changes

- 001-customer-feedback: Added Python 3.12 (backend), TypeScript / Angular 17 (frontend) + FastAPI, Supabase (PostgreSQL + Storage + Auth), Angular Material
- 013-feedback-rich-media: Added MediaRecorder API (VideoRecorderService), multi-image sequential upload, Supabase Storage bucket updated to 100 MB / video MIME types, feedback_images table (migration 010)
- 014-feedback-threading: Added Supabase Realtime (WebSocket) for live thread updates and notifications, feedback_replies + feedback_notifications tables (migration 011), FeedbackRealtimeService, shared ThreadComponent, /my-feedback route (AuthGuard), notification badge in nav

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
