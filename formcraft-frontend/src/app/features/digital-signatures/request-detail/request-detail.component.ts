import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DigitalSignatureService } from '../../../core/services/digital-signature.service';

@Component({
  selector: 'app-request-detail',
  template: `
    <div class="container" *ngIf="request">
      <h2>{{ 'SIGNATURE.REQUEST_DETAIL' | translate }}</h2>
      <p><strong>{{ 'SIGNATURE.STATUS' | translate }}:</strong> {{ request.status }}</p>
      <p><strong>{{ 'SIGNATURE.EXPIRES_AT' | translate }}:</strong> {{ request.expires_at }}</p>

      <h3>{{ 'SIGNATURE.RECIPIENTS' | translate }}</h3>
      <mat-list>
        <mat-list-item *ngFor="let r of request.recipients">
          {{ r.name }} - {{ r.status }}
          <button mat-button *ngIf="r.status === 'invited'" (click)="resend(r.id)">
            {{ 'SIGNATURE.RESEND' | translate }}
          </button>
        </mat-list-item>
      </mat-list>

      <h3>{{ 'SIGNATURE.EVENTS' | translate }}</h3>
      <mat-list>
        <mat-list-item *ngFor="let e of request.events">
          {{ e.event_type }} - {{ e.created_at }}
        </mat-list-item>
      </mat-list>

      <button mat-raised-button color="warn" (click)="cancel()">
        {{ 'SIGNATURE.CANCEL' | translate }}
      </button>
    </div>
  `,
  standalone: false,
})
export class RequestDetailComponent implements OnInit {
  request: any;

  constructor(private route: ActivatedRoute, private service: DigitalSignatureService) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.service.getRequest(id).subscribe((res) => {
        this.request = res;
      });
    }
  }

  resend(recipientId: string): void {
    if (!this.request) return;
    this.service.resendInvitation(this.request.id, recipientId).subscribe();
  }

  cancel(): void {
    if (!this.request) return;
    this.service.cancelRequest(this.request.id).subscribe(() => {
      // refresh
      this.ngOnInit();
    });
  }
}
