import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { PlatformService } from '../../../core/services/platform.service';
import { OrganizationDetail } from '../../../shared/models/platform.models';

@Component({
  selector: 'app-organization-detail',
  template: `
    <div class="detail-container" *ngIf="org">
      <h1>{{ org.name_ar }}</h1>

      <mat-tab-group>
        <mat-tab [label]="'PLATFORM.TAB_PROFILE' | translate">
          <app-profile-tab [org]="org"></app-profile-tab>
        </mat-tab>
        <mat-tab [label]="'PLATFORM.TAB_SUBSCRIPTION' | translate">
          <app-subscription-tab [org]="org"></app-subscription-tab>
        </mat-tab>
        <mat-tab [label]="'PLATFORM.TAB_USERS' | translate">
          <app-users-tab [org]="org"></app-users-tab>
        </mat-tab>
        <mat-tab [label]="'PLATFORM.TAB_STATS' | translate">
          <app-stats-tab [org]="org"></app-stats-tab>
        </mat-tab>
      </mat-tab-group>
    </div>
  `,
  styles: [
    `.detail-container { padding: 16px; }`,
  ],
})
export class OrganizationDetailComponent implements OnInit {
  org: OrganizationDetail | null = null;

  constructor(
    private route: ActivatedRoute,
    private platformService: PlatformService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.platformService.getOrganization(id).subscribe((org) => {
        this.org = org;
      });
    }
  }
}
