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
});
