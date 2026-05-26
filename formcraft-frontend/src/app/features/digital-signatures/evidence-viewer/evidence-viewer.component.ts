import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DigitalSignatureService } from '../../../core/services/digital-signature.service';

@Component({
  selector: 'app-evidence-viewer',
  template: `
    <div class="container" *ngIf="evidence">
      <h2>{{ 'SIGNATURE.EVIDENCE' | translate }}</h2>
      <p><strong>{{ 'SIGNATURE.DOCUMENT_HASH' | translate }}:</strong> {{ evidence.document_hash }}</p>
      <p><strong>{{ 'SIGNATURE.INTEGRITY' | translate }}:</strong> {{ evidence.integrity_status }}</p>
      <button mat-raised-button color="primary" (click)="verify()">
        {{ 'SIGNATURE.VERIFY_INTEGRITY' | translate }}
      </button>

      <h3>{{ 'SIGNATURE.SIGNERS' | translate }}</h3>
      <mat-list>
        <mat-list-item *ngFor="let s of evidence.signer_snapshot">
          {{ s.name }} - {{ s.signed_at }}
        </mat-list-item>
      </mat-list>

      <h3>{{ 'SIGNATURE.EVENTS' | translate }}</h3>
      <mat-list>
        <mat-list-item *ngFor="let e of evidence.event_summary">
          {{ e.type }} - {{ e.at }}
        </mat-list-item>
      </mat-list>
    </div>
  `,
  standalone: false,
})
export class EvidenceViewerComponent implements OnInit {
  evidence: any;

  constructor(private route: ActivatedRoute, private service: DigitalSignatureService) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.service.getEvidence(id).subscribe((res) => {
        this.evidence = res;
      });
    }
  }

  verify(): void {
    if (!this.evidence) return;
    this.service.verifyEvidence(this.evidence.request_id).subscribe((res) => {
      this.evidence.integrity_status = res.integrity_status;
    });
  }
}
