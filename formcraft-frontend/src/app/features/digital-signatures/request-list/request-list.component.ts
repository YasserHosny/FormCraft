import { Component, OnInit } from '@angular/core';
import { DigitalSignatureService } from '../../../core/services/digital-signature.service';

@Component({
  selector: 'app-request-list',
  template: `
    <div class="container">
      <h2>{{ 'SIGNATURE.REQUEST_LIST' | translate }}</h2>
      <mat-table [dataSource]="requests" class="mat-elevation-z2">
        <ng-container matColumnDef="id">
          <mat-header-cell *matHeaderCellDef>ID</mat-header-cell>
          <mat-cell *matCellDef="let row">{{ row.id }}</mat-cell>
        </ng-container>
        <ng-container matColumnDef="status">
          <mat-header-cell *matHeaderCellDef>{{ 'SIGNATURE.STATUS' | translate }}</mat-header-cell>
          <mat-cell *matCellDef="let row">{{ row.status }}</mat-cell>
        </ng-container>
        <ng-container matColumnDef="expires_at">
          <mat-header-cell *matHeaderCellDef>{{ 'SIGNATURE.EXPIRES_AT' | translate }}</mat-header-cell>
          <mat-cell *matCellDef="let row">{{ row.expires_at }}</mat-cell>
        </ng-container>
        <mat-header-row *matHeaderRowDef="displayedColumns"></mat-header-row>
        <mat-row *matRowDef="let row; columns: displayedColumns;" [routerLink]="['requests', row.id]"></mat-row>
      </mat-table>
    </div>
  `,
  standalone: false,
})
export class RequestListComponent implements OnInit {
  requests: any[] = [];
  displayedColumns = ['id', 'status', 'expires_at'];

  constructor(private service: DigitalSignatureService) {}

  ngOnInit(): void {
    this.service.listRequests().subscribe((res: any) => {
      this.requests = res?.items || [];
    });
  }
}
