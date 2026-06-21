import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { of, throwError } from 'rxjs';
import { BillingService } from '../../../core/services/billing.service';
import { BillingPageComponent } from './billing-page.component';
import { BillingOptionsResponse, SubscriptionResponse } from '../../../shared/models/billing.models';

const NOW = '2026-06-21T00:00:00.000Z';

function makeOptions(): BillingOptionsResponse {
  return {
    currency: 'EGP',
    current_tier: 'starter',
    tiers: [
      { tier: 'professional', amount_minor: 490000, currency: 'EGP', available: true },
      { tier: 'enterprise', amount_minor: 990000, currency: 'EGP', available: true },
    ],
    addons: [],
  } as any;
}

function makeSub(overrides: Partial<SubscriptionResponse> = {}): SubscriptionResponse {
  return {
    id: 'sub-uuid-001',
    org_id: 'org-uuid-001',
    tier: 'professional',
    billing_interval: 'monthly',
    status: 'active',
    current_period_start: NOW,
    current_period_end: NOW,
    next_renewal_amount_minor: 490000,
    currency: 'EGP',
    scheduled_downgrade_tier: null,
    cancel_at_period_end: false,
    failed_payment_count: 0,
    provider_subscription_id: 'sub_1ABC',
    ...overrides,
  } as any;
}

describe('BillingPageComponent', () => {
  let component: BillingPageComponent;
  let fixture: ComponentFixture<BillingPageComponent>;
  let billingSpy: jasmine.SpyObj<BillingService>;
  let dialogSpy: jasmine.SpyObj<MatDialog>;

  beforeEach(async () => {
    billingSpy = jasmine.createSpyObj<BillingService>('BillingService', [
      'getOptions',
      'getCurrentSubscription',
      'scheduleDowngrade',
      'cancelDowngradeSchedule',
      'cancelSubscription',
      'reactivateSubscription',
      'getPortalUrl',
    ]);
    dialogSpy = jasmine.createSpyObj<MatDialog>('MatDialog', ['open']);

    billingSpy.getOptions.and.returnValue(of(makeOptions()));
    billingSpy.getCurrentSubscription.and.returnValue(of(null));

    await TestBed.configureTestingModule({
      declarations: [BillingPageComponent],
      providers: [
        { provide: BillingService, useValue: billingSpy },
        { provide: MatDialog, useValue: dialogSpy },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(BillingPageComponent);
    component = fixture.componentInstance;
  });

  // ---------------------------------------------------------------------------
  // ngOnInit
  // ---------------------------------------------------------------------------

  it('loads billing options on init', () => {
    fixture.detectChanges();
    expect(billingSpy.getOptions).toHaveBeenCalledTimes(1);
    expect(component.options?.currency).toBe('EGP');
    expect(component.loading).toBeFalse();
  });

  it('loads current subscription on init', () => {
    const sub = makeSub();
    billingSpy.getCurrentSubscription.and.returnValue(of(sub));
    fixture.detectChanges();
    expect(component.currentSubscription?.tier).toBe('professional');
  });

  it('sets currentSubscription to null when API returns 404', () => {
    billingSpy.getCurrentSubscription.and.returnValue(throwError(() => ({ status: 404 })));
    fixture.detectChanges();
    expect(component.currentSubscription).toBeNull();
  });

  it('clears loading on options API error', () => {
    billingSpy.getOptions.and.returnValue(throwError(() => new Error('network')));
    fixture.detectChanges();
    expect(component.loading).toBeFalse();
  });

  // ---------------------------------------------------------------------------
  // buyTier — subscribe mode (no active subscription)
  // ---------------------------------------------------------------------------

  it('opens subscribe dialog when no active subscription', () => {
    fixture.detectChanges();
    const dialogRef = { afterClosed: () => of({}) } as MatDialogRef<any>;
    dialogSpy.open.and.returnValue(dialogRef);

    component.buyTier('professional');

    expect(dialogSpy.open).toHaveBeenCalledTimes(1);
    const callArgs = dialogSpy.open.calls.mostRecent().args[1];
    expect(callArgs?.data?.mode).toBe('subscribe');
    expect(callArgs?.data?.tier).toBe('professional');
  });

  it('reloads after subscribe dialog closes with subscribed=true', () => {
    fixture.detectChanges();
    spyOn(component, 'ngOnInit').and.callThrough();
    const dialogRef = { afterClosed: () => of({ subscribed: true }) } as MatDialogRef<any>;
    dialogSpy.open.and.returnValue(dialogRef);

    component.buyTier('professional');

    expect(component.ngOnInit).toHaveBeenCalled();
  });

  it('does not reload when subscribe dialog is dismissed', () => {
    fixture.detectChanges();
    spyOn(component, 'ngOnInit');
    const dialogRef = { afterClosed: () => of(null) } as MatDialogRef<any>;
    dialogSpy.open.and.returnValue(dialogRef);

    component.buyTier('professional');

    expect(component.ngOnInit).not.toHaveBeenCalled();
  });

  // ---------------------------------------------------------------------------
  // buyTier — upgrade mode (active subscription)
  // ---------------------------------------------------------------------------

  it('opens upgrade dialog when active subscription exists', () => {
    billingSpy.getCurrentSubscription.and.returnValue(of(makeSub()));
    fixture.detectChanges();
    const dialogRef = { afterClosed: () => of({}) } as MatDialogRef<any>;
    dialogSpy.open.and.returnValue(dialogRef);

    component.buyTier('enterprise');

    const callArgs = dialogSpy.open.calls.mostRecent().args[1];
    expect(callArgs?.data?.mode).toBe('upgrade');
    expect(callArgs?.data?.tier).toBe('enterprise');
  });

  it('reloads after upgrade dialog closes with upgraded=true', () => {
    billingSpy.getCurrentSubscription.and.returnValue(of(makeSub()));
    fixture.detectChanges();
    spyOn(component, 'ngOnInit').and.callThrough();
    const dialogRef = { afterClosed: () => of({ upgraded: true }) } as MatDialogRef<any>;
    dialogSpy.open.and.returnValue(dialogRef);

    component.buyTier('enterprise');

    expect(component.ngOnInit).toHaveBeenCalled();
  });

  it('opens subscribe (not upgrade) dialog when subscription is cancelled', () => {
    billingSpy.getCurrentSubscription.and.returnValue(of(makeSub({ status: 'cancelled' })));
    fixture.detectChanges();
    const dialogRef = { afterClosed: () => of({}) } as MatDialogRef<any>;
    dialogSpy.open.and.returnValue(dialogRef);

    component.buyTier('professional');

    const callArgs = dialogSpy.open.calls.mostRecent().args[1];
    expect(callArgs?.data?.mode).toBe('subscribe');
  });

  // ---------------------------------------------------------------------------
  // scheduleDowngrade
  // ---------------------------------------------------------------------------

  it('calls billing.scheduleDowngrade and reloads on success', () => {
    billingSpy.scheduleDowngrade.and.returnValue(of({} as any));
    spyOn(component, 'ngOnInit').and.callThrough();
    fixture.detectChanges();

    component.scheduleDowngrade('starter');

    expect(billingSpy.scheduleDowngrade).toHaveBeenCalledWith({ tier: 'starter' });
    expect(component.subLoading).toBeFalse();
  });

  it('clears subLoading on scheduleDowngrade error', () => {
    billingSpy.scheduleDowngrade.and.returnValue(throwError(() => new Error()));
    fixture.detectChanges();

    component.scheduleDowngrade('starter');

    expect(component.subLoading).toBeFalse();
  });

  // ---------------------------------------------------------------------------
  // cancelScheduledDowngrade
  // ---------------------------------------------------------------------------

  it('calls billing.cancelDowngradeSchedule and reloads on success', () => {
    billingSpy.cancelDowngradeSchedule.and.returnValue(of({} as any));
    spyOn(component, 'ngOnInit').and.callThrough();
    fixture.detectChanges();

    component.cancelScheduledDowngrade();

    expect(billingSpy.cancelDowngradeSchedule).toHaveBeenCalledTimes(1);
    expect(component.subLoading).toBeFalse();
  });

  // ---------------------------------------------------------------------------
  // cancelSubscription
  // ---------------------------------------------------------------------------

  it('calls billing.cancelSubscription and resets cancelConfirming on success', () => {
    billingSpy.cancelSubscription.and.returnValue(of({} as any));
    fixture.detectChanges();
    component.cancelConfirming = true;

    component.cancelSubscription();

    expect(billingSpy.cancelSubscription).toHaveBeenCalledTimes(1);
    expect(component.cancelConfirming).toBeFalse();
    expect(component.subLoading).toBeFalse();
  });

  it('clears subLoading on cancelSubscription error', () => {
    billingSpy.cancelSubscription.and.returnValue(throwError(() => new Error()));
    fixture.detectChanges();

    component.cancelSubscription();

    expect(component.subLoading).toBeFalse();
  });

  // ---------------------------------------------------------------------------
  // reactivateSubscription
  // ---------------------------------------------------------------------------

  it('calls billing.reactivateSubscription and reloads on success', () => {
    billingSpy.reactivateSubscription.and.returnValue(of({} as any));
    spyOn(component, 'ngOnInit').and.callThrough();
    fixture.detectChanges();

    component.reactivateSubscription();

    expect(billingSpy.reactivateSubscription).toHaveBeenCalledTimes(1);
    expect(component.subLoading).toBeFalse();
  });

  // ---------------------------------------------------------------------------
  // openPaymentPortal
  // ---------------------------------------------------------------------------

  it('opens portal URL in a new tab', () => {
    const openSpy = spyOn(window, 'open');
    billingSpy.getPortalUrl.and.returnValue(
      of({ portal_url: 'https://billing.stripe.com/session/xyz', expires_at: NOW } as any),
    );
    fixture.detectChanges();

    component.openPaymentPortal();

    expect(openSpy).toHaveBeenCalledWith('https://billing.stripe.com/session/xyz', '_blank');
  });

  // ---------------------------------------------------------------------------
  // Computed getters
  // ---------------------------------------------------------------------------

  it('renewalDate returns the date part of current_period_end', () => {
    billingSpy.getCurrentSubscription.and.returnValue(of(makeSub({ current_period_end: '2026-07-21T12:00:00Z' })));
    fixture.detectChanges();

    expect(component.renewalDate).toBe('2026-07-21');
  });

  it('renewalDate returns empty string when no subscription', () => {
    fixture.detectChanges();
    expect(component.renewalDate).toBe('');
  });

  it('downgradeDate returns the date part of current_period_end', () => {
    billingSpy.getCurrentSubscription.and.returnValue(of(makeSub({ current_period_end: '2026-07-21T12:00:00Z' })));
    fixture.detectChanges();

    expect(component.downgradeDate).toBe('2026-07-21');
  });
});
