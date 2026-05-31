# Quickstart: New Theme Desk Live Data Integration

**Feature**: 050-new-theme-desk-data

## Prerequisites

- Node.js 18+ and npm
- Python 3.12+ with uvicorn
- Both backend and frontend dev servers running

## Start Development

```bash
# Terminal 1: Backend
cd formcraft-backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd formcraft-frontend
npx ng serve --proxy-config proxy.conf.json --port 4200
```

## Key Files to Modify

| File | What to Do |
|------|-----------|
| `ui-redesign/desk/dashboard.component.ts` | Replace mock arrays with DeskService/HistoryService calls |
| `ui-redesign/desk/dashboard.component.html` | Bind template variables instead of hardcoded values |
| `ui-redesign/desk/form-filler.component.ts` | Wire FormFillerService, ConditionEngine, AutoFill, Tafqeet, Validation, Submission |
| `ui-redesign/desk/form-filler.component.html` | Render dynamic fields from template structure |
| `ui-redesign/desk/customers.component.ts` | Replace CUSTOMERS mock import with CustomerService |
| `ui-redesign/desk/customers.component.html` | Bind real customer data |
| `ui-redesign/shared/mock-data.ts` | DELETE this file |

## Services to Import (all providedIn: 'root')

```typescript
import { DeskService } from '../../desk/services/desk.service';
import { DraftService } from '../../desk/services/draft.service';
import { HistoryService } from '../../desk/services/history.service';
import { FormFillerService } from '../../desk/services/form-filler.service';
import { SubmissionService } from '../../desk/services/submission.service';
import { CustomerService } from '../../desk/services/customer.service';
import { AutoFillService } from '../../desk/services/auto-fill.service';
import { ConditionEngineService } from '../../desk/services/condition-engine.service';
import { ValidationService } from '../../desk/services/validation.service';
import { FillerTafqeetService } from '../../desk/services/filler-tafqeet.service';
```

## Verification Steps

1. Navigate to `http://localhost:4200/ui/desk`
2. Dashboard should show real KPIs, pinned templates, recent activity, and drafts
3. Click a template → form filler should render real fields
4. Fill fields → validation and conditional logic should work
5. Save as draft → draft should appear on dashboard
6. Submit → submission should appear in history
7. Navigate to `/ui/desk/customers` → real customer list should appear

## Test Credentials

- **Email**: yasser2006_6@yahoo.com
- **Password**: FormCraft@2026
- **Role**: admin
