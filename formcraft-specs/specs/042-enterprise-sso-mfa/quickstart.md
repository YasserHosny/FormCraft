# Quickstart: Enterprise SSO and MFA

## Integration Scenarios

### Scenario 1: First-Time SAML Configuration

1. Org admin navigates to **Settings > Identity Providers**.
2. Clicks **Add Provider**, selects **SAML**.
3. Enters:
   - Name: "Corporate Azure AD"
   - Domains: `["corp.example.com"]`
   - Metadata URL: `https://login.microsoftonline.com/.../federationmetadata.xml`
4. System fetches metadata, validates XML signature, and stores config as `is_active=false`.
5. Admin clicks **Activate**. System verifies connectivity and domain DNS TXT record.
6. A user with email `user@corp.example.com` visits the login page.
7. System detects the domain and redirects to the SAML SSO initiation endpoint.
8. User authenticates at corporate IdP.
9. IdP POSTs `SAMLResponse` to `/api/v1/sso/saml/acs`.
10. Backend validates assertion, maps identity groups via `identity_mapping`, provisions user, issues JWT.
11. User lands on their permitted default mode (Designer, Operator, etc.).

### Scenario 2: MFA Enrollment for Admin

1. Org admin enables MFA for the "admin" role in **Auth Policy**.
2. Admin signs in; after SSO/password step, system detects MFA requirement.
3. Frontend redirects to `/mfa/enroll` because no verified enrollment exists.
4. Admin selects **Authenticator App**.
5. Backend creates enrollment, returns QR code URI.
6. Admin scans QR code with authenticator app, enters 6-digit code.
7. Backend verifies code, marks enrollment `is_verified=true`, returns recovery codes.
8. Admin saves recovery codes; enrollment becomes `is_active=true`.
9. On subsequent sign-ins, admin is challenged for TOTP code after primary authentication.

### Scenario 3: Session Timeout and Concurrent Limit

1. Auth policy sets `session_timeout_minutes=480` and `max_concurrent_sessions=2`.
2. User signs in on Laptop A. Session record created.
3. User signs in on Mobile B. Second session record created.
4. User attempts sign-in on Tablet C. System detects 2 active sessions.
5. Oldest session (Laptop A) is revoked; new session created for Tablet C.
6. User on Laptop A makes a request. Middleware checks `last_activity_at` against `session_timeout_minutes` and finds it exceeded.
7. API returns `401` with `X-Session-Expired: true`. Frontend redirects to login.
8. `session_event` records `session_revoke` and `timeout` events.

### Scenario 4: Broken IdP Recovery

1. Admin updates SAML metadata with an invalid certificate.
2. System validation fails; config remains `is_active=false` and last working config is preserved.
3. Existing users continue to sign in via the previously active provider or fallback password login.
4. Audit log records `idp_change` with result `failure` and reason.
5. Admin receives notification and reverts to the previous valid metadata.

### Scenario 5: Identity Group Changes

1. Mapping rule: IdP group `BranchOperators` → role `operator`, department `Sales`, branch `Riyadh-01`.
2. Employee Alice signs in; system provisions her profile with the mapped access.
3. Alice is moved to `HQAdmins` in corporate directory.
4. On next sign-in, `BranchOperators` no longer matches.
5. Fallback policy `strip_access` applies: Alice retains her user account but loses `operator` role and `Riyadh-01` branch.
6. Admin receives an alert: "Alice's identity groups no longer match any active mapping; access stripped."
7. Alice can still sign in but sees only minimal permitted UI (per fallback policy).
