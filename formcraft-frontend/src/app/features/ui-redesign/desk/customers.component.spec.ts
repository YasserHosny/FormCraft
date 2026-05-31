import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CustomersComponent } from './customers.component';
import { RouterTestingModule } from '@angular/router/testing';
import { MatIconModule } from '@angular/material/icon';

describe('CustomersComponent - User Story 6: Real Customer Data', () => {
  let component: CustomersComponent;
  let fixture: ComponentFixture<CustomersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CustomersComponent, RouterTestingModule, MatIconModule],
    }).compileComponents();

    fixture = TestBed.createComponent(CustomersComponent);
    component = fixture.componentInstance;
  });

  describe('Customer List Display', () => {
    it('should display loading state while fetching', () => {
      component.loading = true;
      fixture.detectChanges();

      const loadingState = fixture.nativeElement.querySelector('.loading-state');
      expect(loadingState).toBeTruthy();
    });

    it('should display error state when fetch fails', () => {
      component.loading = false;
      component.error = 'Failed to load customers';
      fixture.detectChanges();

      const errorState = fixture.nativeElement.querySelector('.error-state');
      expect(errorState).toBeTruthy();
      expect(errorState.textContent).toContain('حدث خطأ');
    });

    it('should render customer table when data loaded', () => {
      component.loading = false;
      component.error = null;
      component.customers = [
        { id: '1', name: 'فاطمة', email: 'f@example.com', phone: '+971', status: 'active', color: 'c1' },
      ];
      fixture.detectChanges();

      const table = fixture.nativeElement.querySelector('.fc-table');
      expect(table).toBeTruthy();
    });

    it('should display empty state when no customers', () => {
      component.loading = false;
      component.error = null;
      component.customers = [];
      fixture.detectChanges();

      const emptyState = fixture.nativeElement.querySelector('.empty-state');
      expect(emptyState).toBeTruthy();
    });
  });

  describe('Search Functionality', () => {
    it('should have search input available', () => {
      component.loading = false;
      fixture.detectChanges();

      const searchInput = fixture.nativeElement.querySelector('.fc-search-box input');
      expect(searchInput).toBeTruthy();
    });
  });

  describe('Pagination', () => {
    it('should display pagination controls', () => {
      component.loading = false;
      component.error = null;
      component.customers = Array(50).fill(null).map((_, i) => ({
        id: `${i}`,
        name: `Customer ${i}`,
        email: `c${i}@example.com`,
        phone: '+971',
        status: 'active',
      }));
      fixture.detectChanges();

      const pagination = fixture.nativeElement.querySelector('.pagination');
      expect(pagination).toBeTruthy();
    });
  });
});
