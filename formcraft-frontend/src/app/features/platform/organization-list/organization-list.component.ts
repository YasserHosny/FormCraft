import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { FormControl } from '@angular/forms';
import { debounceTime } from 'rxjs/operators';
import { PlatformService } from '../../../core/services/platform.service';
import { OrganizationSummary, PaginatedOrganizations } from '../../../shared/models/platform.models';

@Component({
  selector: 'app-organization-list',
  template: `
    <div class="org-list-container">
      <div class="toolbar">
        <h1>{{ 'PLATFORM.ORG_LIST_TITLE' | translate }}</h1>
        <button mat-raised-button color="primary" (click)="createOrg()">
          {{ 'PLATFORM.CREATE_ORG' | translate }}
        </button>
      </div>

      <div class="filters">
        <mat-form-field appearance="outline">
          <mat-label>{{ 'PLATFORM.SEARCH' | translate }}</mat-label>
          <input matInput [formControl]="searchControl" placeholder="{{ 'PLATFORM.SEARCH_PLACEHOLDER' | translate }}" />
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'PLATFORM.TIER_FILTER' | translate }}</mat-label>
          <mat-select [formControl]="tierControl">
            <mat-option value="">{{ 'PLATFORM.ALL' | translate }}</mat-option>
            <mat-option value="starter">Starter</mat-option>
            <mat-option value="professional">Professional</mat-option>
            <mat-option value="enterprise">Enterprise</mat-option>
            <mat-option value="platform">Platform</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'PLATFORM.STATUS_FILTER' | translate }}</mat-label>
          <mat-select [formControl]="statusControl">
            <mat-option value="">{{ 'PLATFORM.ALL' | translate }}</mat-option>
            <mat-option value="active">{{ 'PLATFORM.STATUS_ACTIVE' | translate }}</mat-option>
            <mat-option value="suspended">{{ 'PLATFORM.STATUS_SUSPENDED' | translate }}</mat-option>
          </mat-select>
        </mat-form-field>
      </div>

      <table mat-table [dataSource]="orgs" class="mat-elevation-z2">
        <ng-container matColumnDef="name">
          <th mat-header-cell *matHeaderCellDef>{{ 'PLATFORM.ORG_NAME' | translate }}</th>
          <td mat-cell *matCellDef="let org">{{ org.name_ar }}</td>
        </ng-container>

        <ng-container matColumnDef="tier">
          <th mat-header-cell *matHeaderCellDef>{{ 'PLATFORM.TIER' | translate }}</th>
          <td mat-cell *matCellDef="let org">{{ org.subscription_tier }}</td>
        </ng-container>

        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef>{{ 'PLATFORM.STATUS' | translate }}</th>
          <td mat-cell *matCellDef="let org">
            <mat-chip [color]="org.status === 'active' ? 'primary' : 'warn'" selected>
              {{ org.status }}
            </mat-chip>
          </td>
        </ng-container>

        <ng-container matColumnDef="users">
          <th mat-header-cell *matHeaderCellDef>{{ 'PLATFORM.ACTIVE_USERS' | translate }}</th>
          <td mat-cell *matCellDef="let org">{{ org.active_users_count }}</td>
        </ng-container>

        <ng-container matColumnDef="templates">
          <th mat-header-cell *matHeaderCellDef>{{ 'PLATFORM.TEMPLATES' | translate }}</th>
          <td mat-cell *matCellDef="let org">{{ org.templates_count }}</td>
        </ng-container>

        <ng-container matColumnDef="submissions">
          <th mat-header-cell *matHeaderCellDef>{{ 'PLATFORM.SUBMISSIONS_THIS_MONTH' | translate }}</th>
          <td mat-cell *matCellDef="let org">{{ org.submissions_this_month }}</td>
        </ng-container>

        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>{{ 'PLATFORM.ACTIONS' | translate }}</th>
          <td mat-cell *matCellDef="let org">
            <button mat-icon-button (click)="viewOrg(org.id)">
              <mat-icon>visibility</mat-icon>
            </button>
            <button mat-icon-button *ngIf="org.status === 'active'" (click)="suspendOrg(org.id)">
              <mat-icon>block</mat-icon>
            </button>
            <button mat-icon-button *ngIf="org.status === 'suspended'" (click)="reactivateOrg(org.id)">
              <mat-icon>check_circle</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>

      <mat-paginator
        [length]="total"
        [pageSize]="pageSize"
        [pageSizeOptions]="[10, 20, 50]"
        (page)="onPageChange($event)">
      </mat-paginator>
    </div>
  `,
  styles: [
    `.org-list-container { padding: 16px; }`,
    `.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }`,
    `.filters { display: flex; gap: 16px; margin-bottom: 16px; }`,
    `table { width: 100%; }`,
  ],
})
export class OrganizationListComponent implements OnInit {
  orgs: OrganizationSummary[] = [];
  total = 0;
  page = 1;
  pageSize = 20;
  displayedColumns = ['name', 'tier', 'status', 'users', 'templates', 'submissions', 'actions'];

  searchControl = new FormControl('');
  tierControl = new FormControl('');
  statusControl = new FormControl('');

  constructor(private platformService: PlatformService, private router: Router) {}

  ngOnInit(): void {
    this.loadOrgs();

    this.searchControl.valueChanges.pipe(debounceTime(300)).subscribe(() => this.loadOrgs());
    this.tierControl.valueChanges.subscribe(() => this.loadOrgs());
    this.statusControl.valueChanges.subscribe(() => this.loadOrgs());
  }

  loadOrgs(): void {
    this.platformService
      .listOrganizations({
        page: this.page,
        page_size: this.pageSize,
        search: this.searchControl.value || undefined,
        tier: this.tierControl.value || undefined,
        status: this.statusControl.value || undefined,
      })
      .subscribe((res: PaginatedOrganizations) => {
        this.orgs = res.items;
        this.total = res.total;
      });
  }

  onPageChange(event: any): void {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadOrgs();
  }

  createOrg(): void {
    this.router.navigate(['/platform/organizations/create']);
  }

  viewOrg(id: string): void {
    this.router.navigate(['/platform/organizations', id]);
  }

  suspendOrg(id: string): void {
    this.platformService.suspendOrganization(id).subscribe(() => this.loadOrgs());
  }

  reactivateOrg(id: string): void {
    this.platformService.reactivateOrganization(id).subscribe(() => this.loadOrgs());
  }
}
