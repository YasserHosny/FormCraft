# Quick Start: Desk Search & Quick Fill

## Setup

1. Run the database migration:
   ```bash
   cd formcraft-backend
   psql $DATABASE_URL -f migrations/037_desk_search_quickfill.sql
   ```

2. Seed default Quick Fill mappings for existing organizations:
   ```bash
   python scripts/seed_quickfill_mappings.py
   ```

3. Refresh the materialized view:
   ```sql
   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_global_search;
   ```

## Using Global Search

1. Navigate to the Form Desk
2. Click the search bar at the top of the page
3. Type at least 2 characters
4. Results appear grouped by:
   - **Templates** — click to open the template
   - **Submissions** — click to view submission detail
   - **Customers** — click to see customer profile

## Using Quick Fill

1. Select a template (from search or dashboard)
2. Click **Quick Fill** button
3. Search for a customer by name, ID, or phone
4. Select the customer from results
5. The form opens with matching fields pre-filled (light blue background)
6. Edit any field as needed
7. Print or save the form — submission is linked to the customer
8. Optionally click **Save to Profile** to update customer data

## Admin: Customizing Field Mappings

1. Go to **Organization Settings > Quick Fill Mappings**
2. Add or edit mappings:
   - Field Key: the template element key (e.g., `passport_number`)
   - Customer Attribute: the customer profile field (e.g., `identifier`)
3. Changes apply immediately to new Quick Fill sessions

## Testing

```bash
# Backend tests
cd formcraft-backend
pytest tests/unit/test_search_service.py tests/unit/test_quickfill_service.py -v

# Frontend tests
cd formcraft-frontend
ng test --include='**/search/**' --include='**/quickfill/**'
```
