import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { SubmissionConfirmedComponent } from './submission-confirmed.component';

describe('SubmissionConfirmedComponent', () => {
  let component: SubmissionConfirmedComponent;
  let fixture: ComponentFixture<SubmissionConfirmedComponent>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    router = jasmine.createSpyObj<Router>('Router', ['getCurrentNavigation', 'navigate']);
    router.getCurrentNavigation.and.returnValue({
      extras: {
        state: {
          referenceNumber: 'REF-001',
          templateName: 'Template',
          submittedAt: new Date().toISOString(),
        },
      },
    } as any);

    await TestBed.configureTestingModule({
      imports: [SubmissionConfirmedComponent],
      providers: [{ provide: Router, useValue: router }],
    }).compileComponents();

    fixture = TestBed.createComponent(SubmissionConfirmedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('renders reference number from router state', () => {
    expect(component.state?.referenceNumber).toBe('REF-001');
  });

  it('redirects to /ui/desk when state is null', () => {
    router.getCurrentNavigation.and.returnValue({ extras: { state: null } } as any);
    component.ngOnInit();
    expect(router.navigate).toHaveBeenCalledWith(['/ui/desk']);
  });

  it('navigates back to desk on button action', () => {
    component.backToDesk();
    expect(router.navigate).toHaveBeenCalledWith(['/ui/desk']);
  });
});
