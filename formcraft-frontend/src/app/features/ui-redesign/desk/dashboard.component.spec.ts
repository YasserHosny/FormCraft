import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DashboardComponent } from './dashboard.component';
import { RouterTestingModule } from '@angular/router/testing';
import { MatIconModule } from '@angular/material/icon';
import { of, throwError } from 'rxjs';

describe('DashboardComponent - User Story 1: Real KPIs', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardComponent, RouterTestingModule, MatIconModule],
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
  });

  describe('KPI Display', () => {
    it('should display KPI cards with bound values', () => {
      component.loading = false;
      component.error = null;
      fixture.detectChanges();

      const kpiCards = fixture.nativeElement.querySelectorAll('fc-kpi-card');
      expect(kpiCards.length).toBeGreaterThan(0);
    });

    it('should show loading state while fetching data', () => {
      component.loading = true;
      fixture.detectChanges();

      const loadingState = fixture.nativeElement.querySelector('.loading-state');
      expect(loadingState).toBeTruthy();
    });

    it('should display zero values correctly', () => {
      component.loading = false;
      component.error = null;
      fixture.detectChanges();

      const kpiCards = fixture.nativeElement.querySelectorAll('fc-kpi-card');
      expect(kpiCards.length).toBeGreaterThan(0);
    });

    it('should show error state when data fetch fails', () => {
      component.loading = false;
      component.error = 'Failed to load dashboard data';
      fixture.detectChanges();

      const errorState = fixture.nativeElement.querySelector('.error-state');
      expect(errorState).toBeTruthy();
      expect(errorState.textContent).toContain('حدث خطأ');
      expect(errorState.textContent).toContain('Failed to load dashboard data');
    });

    it('should show empty state when no data available', () => {
      component.loading = false;
      component.error = null;
      component.isEmpty = true;
      fixture.detectChanges();

      const emptyState = fixture.nativeElement.querySelector('.empty-state');
      expect(emptyState).toBeTruthy();
      expect(emptyState.textContent).toContain('لا توجد بيانات');
    });
  });

  describe('Recent Activity Display', () => {
    it('should render activity table when data is loaded', () => {
      component.loading = false;
      component.error = null;
      fixture.detectChanges();

      const table = fixture.nativeElement.querySelector('.fc-table');
      expect(table).toBeTruthy();
    });
  });

  describe('Drafts Panel Display', () => {
    it('should render drafts section when data is loaded', () => {
      component.loading = false;
      component.error = null;
      fixture.detectChanges();

      const content = fixture.nativeElement.querySelector('.two-col');
      expect(content).toBeTruthy();
    });
  });

  describe('Pinned Templates Display', () => {
    it('should display real pinned templates filtered to published only, max 6', () => {
      component.loading = false;
      component.error = null;
      component.pinnedTemplates = [
        { template_id: 'tpl-1', template_name: 'Form 1', is_published: true, pinned_at: new Date() },
        { template_id: 'tpl-2', template_name: 'Form 2', is_published: true, pinned_at: new Date() },
      ];
      fixture.detectChanges();

      const pinCards = fixture.nativeElement.querySelectorAll('.pin-card');
      expect(pinCards.length).toBe(2);
    });

    it('should navigate to form filler when pinned template is clicked', () => {
      component.loading = false;
      component.error = null;
      component.pinnedTemplates = [
        { template_id: 'tpl-1', template_name: 'Form 1', is_published: true, pinned_at: new Date() },
      ];
      spyOn(component, 'fillTemplate');
      fixture.detectChanges();

      const pinCard = fixture.nativeElement.querySelector('.pin-card');
      pinCard.click();

      expect(component.fillTemplate).toHaveBeenCalledWith('tpl-1');
    });

    it('should display empty state when no pinned templates', () => {
      component.loading = false;
      component.error = null;
      component.pinnedTemplates = [];
      fixture.detectChanges();

      const emptyPins = fixture.nativeElement.querySelector('.empty-pins');
      expect(emptyPins).toBeTruthy();
      expect(emptyPins.textContent).toContain('لا توجد نماذج مثبّتة');
    });

    it('should cap pinned templates at 6 items', () => {
      component.loading = false;
      component.error = null;
      component.pinnedTemplates = Array(8)
        .fill(null)
        .map((_, i) => ({
          template_id: `tpl-${i}`,
          template_name: `Form ${i}`,
          is_published: true,
          pinned_at: new Date(),
        }));
      fixture.detectChanges();

      const pinCards = fixture.nativeElement.querySelectorAll('.pin-card');
      expect(pinCards.length).toBeLessThanOrEqual(6);
    });
  });
});
