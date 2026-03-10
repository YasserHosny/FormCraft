# Supabase Cloud Setup Guide

## Step 1: Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Sign in or create an account
3. Click **"New Project"**
4. Fill in:
   - **Name**: `formcraft` (or `formcraft-dev`)
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to you (e.g., `eu-central-1` for Europe)
   - **Pricing Plan**: Free tier is fine for development
5. Click **"Create new project"**
6. Wait 2-3 minutes for provisioning

## Step 2: Get Project Credentials

Once the project is ready:

1. Go to **Settings** (gear icon in sidebar) → **API**
2. Copy these values:

```
Project URL: https://xxxxxxxxxxxxx.supabase.co
anon public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (click "Reveal" button)
```

3. Go to **Settings** → **API** → scroll to **JWT Settings**
4. Copy:
```
JWT Secret: your-super-secret-jwt-token-with-at-least-32-characters
```

## Step 3: Run Database Migrations

1. In Supabase Dashboard, go to **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Copy and paste the contents of each migration file in order:

### Migration 001: Create Profiles
```sql
-- Copy contents from: supabase/migrations/001_create_profiles.sql
```

### Migration 002: Create Audit Logs
```sql
-- Copy contents from: supabase/migrations/002_create_audit_logs.sql
```

### Migration 003: Create Templates
```sql
-- Copy contents from: supabase/migrations/003_create_templates.sql
```

### Migration 004: Create Pages
```sql
-- Copy contents from: supabase/migrations/004_create_pages.sql
```

### Migration 005: Create Elements
```sql
-- Copy contents from: supabase/migrations/005_create_elements.sql
```

### Migration 006: RLS Policies
```sql
-- Copy contents from: supabase/migrations/006_rls_policies.sql
```

4. Click **"Run"** for each migration
5. Verify no errors in the output

## Step 4: Verify Tables Created

1. Go to **Table Editor** (left sidebar)
2. You should see these tables:
   - `profiles`
   - `audit_logs`
   - `templates`
   - `pages`
   - `elements`

## Step 5: Create Backend .env File

Paste your credentials here and I'll create the `.env` file:

```
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
SUPABASE_JWT_SECRET=your-jwt-secret
```

## Step 6: Update Frontend Environment (Optional for now)

The frontend is already configured to use `http://localhost:8000` for the backend API, which is correct for local development.

## Step 7: Restart Backend Server

Once `.env` is created, restart the backend server to connect to Supabase Cloud.

## Step 8: Test Authentication

1. Open http://localhost:4200
2. Try to access `/auth/register` (should be restricted to admins)
3. Create first admin user via backend API or Supabase Auth dashboard
4. Login and verify profile is created

---

## Ready to Proceed?

**Please complete Steps 1-2 above**, then paste your credentials here in this format:

```
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
SUPABASE_JWT_SECRET=your-jwt-secret
```

I'll then:
1. Create the `.env` file
2. Provide you with the SQL migration scripts to run
3. Restart the backend server
4. Guide you through creating the first admin user
5. Test the full application end-to-end
