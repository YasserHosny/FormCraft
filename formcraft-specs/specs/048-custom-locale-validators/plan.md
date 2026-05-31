# Feature 048: Implementation Plan

## Goal
Enable organization administrators to create reusable, org-scoped custom validators with bilingual error messages, integrated into both the Design Studio and Form Filler.

## Key Outcomes
1. Org admins can define regex validators with Arabic + English error messages
2. Designers can apply validators from a dropdown in element properties
3. Form operators see bilingual error messages during validation
4. Admins have full audit trail of validator operations and template usage
5. Validators are completely org-scoped (no cross-org leakage)

---

## Architecture Overview

### Data Flow
```
Admin (Create Validator)
  → /admin/validators POST
    → custom_validators table
    → Audit log (VALIDATOR_CREATED)
    
Designer (Apply Validator)
  → GET /api/validators/org
    → Returns custom validators
  → Element properties → select validator
    → element.custom_validators_ids array updated
    
Operator (Validate Form)
  → Form submission
    → Validation engine evaluates custom_validators_ids
    → Regex test against field value
    → Show error_message_ar or error_message_en based on language
```

### System Components
- **Backend API**: Validator CRUD, RLS policies, audit logging
- **Admin Console**: List, create, edit, delete validators; view template usage
- **Design Studio**: Element properties panel with validator dropdown
- **Form Filler**: Validation engine integration, bilingual error display

---

## Implementation Timeline

### Week 1: Foundation (Phase 1 - Data Model & API)

**Day 1-2: Database & Migrations**
- Create custom_validators table migration
- Add custom_validators_ids to elements table
- Create indexes for performance
- Write and test RLS policies

**Day 3: Backend API - Validator CRUD**
- Implement GET /admin/validators (list with pagination, search)
- Implement POST /admin/validators (create with validation)
- Implement GET /admin/validators/:id (single validator)
- Implement PUT /admin/validators/:id (update)
- Implement DELETE /admin/validators/:id (soft delete)

**Day 4: Backend API - Discovery & Usage**
- Implement GET /api/validators/org (for designers)
- Implement GET /admin/validators/:id/templates (usage tracking)
- Add response caching for fast dropdown load

**Day 5: Audit Logging & Integration**
- Implement audit logging for VALIDATOR_CREATED, VALIDATOR_UPDATED, VALIDATOR_DELETED
- Add regex pattern validation before storage
- Add rate limiting for API endpoints
- Write integration tests for Phase 1

### Week 2: Admin Interface (Phase 2 - Admin UI)

**Day 1: Admin Page Scaffold**
- Create /admin/validators route
- Build page layout: list + detail panels
- Add toolbar with search, filter, create button
- Wire up list API calls

**Day 2: List Component**
- Implement table/grid of validators
- Add pagination, search by name
- Add sort by name, created_at, updated_at
- Add row action buttons (edit, delete, view usage)

**Day 3: Create/Edit Modals**
- Create form component for new validator
- Add regex pattern tester (validate before save)
- Bilingual input fields (AR/EN side-by-side)
- Error handling and validation feedback

**Day 4: Delete & Usage**
- Delete confirmation dialog with template count
- Usage tab showing templates using validator
- Links to edit each template using the validator

**Day 5: Polish & Testing**
- Toast notifications for create/update/delete
- Loading states and error states
- Audit trail view for validator operations
- Write E2E tests for admin workflows

### Week 3: Designer Integration (Phase 3 - Designer UI)

**Day 1: Element Properties Extension**
- Add "Custom Validators" section to properties panel
- Wire up dropdown to fetch from GET /api/validators/org
- Handle loading and empty states

**Day 2: Dropdown & Selection**
- Implement searchable dropdown component
- Show validator name and description
- Support multiple selections
- Add visual indicator for selected validators

**Day 3: Tag UI & Persistence**
- Display selected validators as removable chips
- Implement removal logic (update custom_validators_ids array)
- Save changes to element
- Handle undo/redo

**Day 4: Preview & Documentation**
- Update element preview to show custom validators applied
- Add tooltip with validator regex pattern and description
- Update designer guides

**Day 5: Testing & Integration**
- Unit tests for dropdown and tag UI
- Integration tests: save template with validators
- E2E tests: designer workflow end-to-end

### Week 4: Form Filler Integration (Phase 4 - Validation Engine)

**Day 1: Validation Engine Extension**
- Extend form validator to check custom_validators_ids
- Implement regex evaluation logic
- Test regex pattern matching

**Day 2: Bilingual Error Messages**
- Fetch operator's language preference
- Select error_message_ar or error_message_en
- Display error inline next to field

**Day 3: Real-Time Validation**
- Implement on-field-change validation
- Show/hide error messages as operator types
- Update visual feedback

**Day 4: Form Submission Handler**
- Validate all custom validators before submit
- Prevent submission if any validator fails
- Show all validation errors together

**Day 5: Testing**
- Unit tests for validation logic
- E2E tests: operator submits invalid data, sees error, corrects, resubmits
- Test bilingual error messages

### Week 5: Testing, Documentation & Refinement (Phase 5)

**Day 1-2: Comprehensive Testing**
- Performance testing with 100+ validators per org
- Load testing for dropdown population
- Stress testing for form submission with 10+ validators/field
- Security testing for ReDoS vulnerability

**Day 3: Documentation**
- API documentation with example requests/responses
- Admin guide for creating validators
- Designer guide for using validators
- Operator guide for validation feedback

**Day 4: Refinement & Bug Fixes**
- Address bugs found in testing
- Performance optimizations (caching, indexing)
- UX polish based on feedback

**Day 5: Final QA & Sign-Off**
- Final E2E test runs
- Production readiness checklist
- Prepare release notes

---

## Risk Management

### Risk 1: ReDoS (Regular Expression Denial of Service)
**Impact**: High (API could be exploited with malicious regex)  
**Mitigation**:
- Validate regex patterns before storage (test execution time)
- Set timeout on regex evaluation (max 100ms)
- Rate limit /admin/validators POST endpoint
- Document recommended regex patterns
- Monitor regex execution time in production

### Risk 2: Performance Degradation with Many Validators
**Impact**: Medium (slow dropdown or validation)  
**Mitigation**:
- Index (org_id, name) for fast lookups
- Cache validator list in memory per org
- Lazy load validator descriptions in dropdown
- Measure performance with 100+ validators
- Set up monitoring for query times

### Risk 3: Cross-Org Validator Leakage
**Impact**: Critical (data exposure)  
**Mitigation**:
- Implement RLS policies strictly
- Test org isolation thoroughly (unit + integration tests)
- Code review all query logic
- Audit log all access attempts
- Monitor for unauthorized access in production

### Risk 4: Validator Update Breaking Templates
**Impact**: Medium (templates using validator may fail validation)  
**Mitigation**:
- Soft delete validators (never truly delete)
- Maintain audit trail of all changes
- Provide admin rollback capability (if needed)
- Test update propagation thoroughly

### Risk 5: Bilingual Message Fallback Failures
**Impact**: Low (operator sees wrong language error)  
**Mitigation**:
- Always provide both AR and EN messages (required field)
- Default to English if operator's language unavailable
- Log missing language errors
- Monitor for language selection issues

---

## Dependencies & Prerequisites

### External Dependencies
- Existing organizations, profiles, elements tables
- Existing audit logging infrastructure
- Existing form validation engine
- Existing form filler implementation

### Internal Dependencies
- **Phases 1 → 2, 3, 4**: Data model must be ready before any other phase
- **Phases 2 & 3**: Can progress in parallel (separate UI concerns)
- **Phase 4**: Requires Phase 1 complete (needs data model)
- **Phase 5**: Requires Phases 1-4 feature-complete

### Team Requirements
- 1 Backend Developer (Phase 1)
- 2 Frontend Developers (Phases 2, 3, 4)
- 1 QA/Test Automation Engineer (Phase 5)
- 1 Technical Writer (Phase 5 - documentation)

---

## Success Metrics

### Functional Success
- ✅ All endpoints tested and working
- ✅ RLS policies prevent cross-org access (100% isolation)
- ✅ Validators appear in Designer dropdown immediately after creation
- ✅ Form filler validates against custom validators correctly
- ✅ Bilingual error messages display in operator's language
- ✅ Audit trail captures all CRUD operations

### Performance Success
- ✅ Validator dropdown loads in < 200ms (with 100 validators)
- ✅ Form field validation < 100ms (with 10 validators/field)
- ✅ Admin list page loads in < 500ms (with 1000 validators)
- ✅ Regex evaluation timeout prevents ReDoS attacks

### Quality Success
- ✅ 95%+ test coverage for custom validator code paths
- ✅ 0 security vulnerabilities (ReDoS, cross-org leakage, SQL injection)
- ✅ 0 critical bugs in production for 2 weeks post-launch
- ✅ User documentation complete and clear

### Adoption Success
- ✅ All admins can create validators without support
- ✅ All designers understand how to apply validators
- ✅ All operators understand validation errors
- ✅ Feedback rating ≥ 4/5 from early adopters

---

## Rollback Plan

If critical issues are discovered post-launch:

1. **Minor bugs** (e.g., UI layout, typos): Fix forward in hotfix PR
2. **Performance issues** (e.g., slow dropdown): Deploy caching/indexing fix
3. **Security issues** (e.g., cross-org leakage): Immediately revert, investigate, fix, redeploy
4. **Data corruption**: Restore from backup, investigate cause, redeploy with fix

**Automatic rollback triggers**:
- ReDoS attack detected → disable /admin/validators endpoints
- Cross-org data leakage → disable validator functionality, alert security team
- Form submission validation failure > 5% → investigate cause, consider rollback

---

## Post-Launch Monitoring

### Metrics to Track
- API endpoint latency (GET /admin/validators, POST /admin/validators, GET /api/validators/org)
- Regex evaluation time distribution
- Validator creation/update frequency
- Template adoption (% of templates using custom validators)
- Form submission validation error rates
- User feedback and support tickets

### Alerts
- Regex evaluation time > 500ms
- Cross-org access attempts
- Audit log missing entries
- API endpoint latency > 1s
- Form submission failures > 5%

---

## Next Steps (Post-Phase 5)

1. **Monitor production** for 2 weeks, address any issues
2. **Gather user feedback** from admins, designers, operators
3. **Plan Phase 2 enhancements**:
   - Regex library (pre-built validators for common patterns)
   - Validator groups (organize validators by category)
   - Conditional validators (apply based on other field values)
   - A/B testing for error message effectiveness
