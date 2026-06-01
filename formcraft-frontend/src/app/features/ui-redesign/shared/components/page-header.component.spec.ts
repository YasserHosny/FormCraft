import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';

import { PageHeaderComponent } from './page-header.component';

@Component({
  standalone: true,
  imports: [PageHeaderComponent],
  template: `
    <fc-page-header title="Templates" subtitle="Manage templates">
      <div actions>
        <button class="fc-btn outline" type="button">Export</button>
        <button class="fc-btn outline" type="button">Import PDF</button>
        <button class="fc-btn primary" type="button">Create New Template</button>
      </div>
    </fc-page-header>
  `,
})
class PageHeaderActionsHostComponent {}

describe('PageHeaderComponent', () => {
  let fixture: ComponentFixture<PageHeaderActionsHostComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PageHeaderActionsHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(PageHeaderActionsHostComponent);
    fixture.detectChanges();
  });

  it('lays out projected action buttons with consistent spacing', () => {
    const actions = fixture.debugElement.query(By.css('[actions]')).nativeElement as HTMLElement;
    const primaryAction = fixture.debugElement.query(By.css('.fc-btn.primary')).nativeElement as HTMLElement;

    expect(getComputedStyle(actions).display).toBe('flex');
    expect(getComputedStyle(actions).gap).toBe('8px');
    expect(getComputedStyle(primaryAction).marginInlineStart).toBe('8px');
  });
});
