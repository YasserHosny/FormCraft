# Supabase Local Setup Instructions

## Prerequisites Completed
- ✅ Supabase CLI v2.75.0 installed at `~/.local/bin/supabase`
- ✅ User added to docker group: `sudo usermod -aG docker yasser`
- ⚠️ **You need to logout and login again** for docker group to take effect

## After Re-login, Run These Commands:

### 1. Verify Docker Access
```bash
docker ps
# Should show running containers without "permission denied"
```

### 2. Start Supabase Local Stack
```bash
cd /media/yasser/Work/Projects/formcraft-backend
export PATH="$HOME/.local/bin:$PATH"
supabase start
```

This will:
- Pull Docker images (postgres, gotrue, realtime, storage, etc.)
- Start ~10 containers
- Output credentials like:
  ```
  API URL: http://localhost:54321
  DB URL: postgresql://postgres:postgres@localhost:54322/postgres
  Studio URL: http://localhost:54323
  anon key: eyJhbGc...
  service_role key: eyJhbGc...
  ```

### 3. Copy Migrations to Supabase Directory
```bash
cd /media/yasser/Work/Projects/formcraft-backend
cp supabase/migrations/*.sql supabase/migrations/
```

### 4. Run Migrations
```bash
supabase db reset
# Or manually apply each migration:
# supabase db push
```

### 5. Create Backend .env File
```bash
cd /media/yasser/Work/Projects/formcraft-backend
cat > .env << 'EOF'
# Supabase Local
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=<paste anon key from supabase start output>
SUPABASE_SERVICE_KEY=<paste service_role key from supabase start output>
SUPABASE_JWT_SECRET=super-secret-jwt-token-with-at-least-32-characters-long

# AWS Bedrock (optional for now)
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
AWS_ACCESS_KEY_ID=placeholder
AWS_SECRET_ACCESS_KEY=placeholder

# App
CORS_ORIGINS=http://localhost:4200
LOG_LEVEL=info
APP_VERSION=0.1.0
EOF
```

### 6. Update Frontend Environment
```bash
cd /media/yasser/Work/Projects/formcraft-frontend
# Edit src/environments/environment.ts to point to http://localhost:8000
```

### 7. Restart Backend Server
```bash
cd /media/yasser/Work/Projects/formcraft-backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 8. Test End-to-End
1. Open http://localhost:4200
2. Try to register a new admin user (will fail until backend connects to Supabase)
3. Login with created user
4. Create a template
5. Open designer

## Troubleshooting

### Docker Permission Still Denied
```bash
# Verify group membership
groups
# Should show "docker" in the list

# If not, try:
sudo systemctl restart docker
newgrp docker
```

### Supabase Containers Not Starting
```bash
# Check Docker resources
docker system df
docker system prune -a  # If low on space

# View logs
supabase status
docker logs supabase_db_formcraft-backend
```

### Migrations Not Applied
```bash
# Check current migration status
supabase migration list

# Apply specific migration
supabase db push --include-all
```

## Supabase Cloud Setup (Later)

When ready for staging/production:

1. Go to https://supabase.com/dashboard
2. Create new project
3. Copy credentials from Settings > API
4. Update backend .env with cloud credentials
5. Run migrations via SQL Editor or `supabase db push --linked`
6. Update frontend environment.prod.ts with production API URL

## Current Status
- Local Supabase: Pending (requires re-login for docker permissions)
- Backend tests: 58/58 passing ✅
- Frontend build: Successful ✅
- Dev servers: Running (frontend :4200, backend :8000) ✅
