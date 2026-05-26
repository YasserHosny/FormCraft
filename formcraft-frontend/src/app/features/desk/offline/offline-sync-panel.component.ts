import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { OfflineSyncService, OfflineSyncState } from './offline-sync.service';

@Component({
  selector: 'fc-offline-sync-panel',
  template: `
    <section class="offline-sync" *ngIf="state$ | async as state" [class.offline]="!state.online" [class.has-conflict]="state.conflicts.length > 0">
      <div class="offline-sync__main">
        <mat-icon>{{ state.online ? 'cloud_done' : 'cloud_off' }}</mat-icon>
        <span>{{ (state.online ? 'offline.online' : 'offline.offline') | translate }}</span>
        <span class="offline-sync__count" *ngIf="state.pending > 0">{{ 'offline.pending_count' | translate:{count: state.pending} }}</span>
      </div>
      <button mat-icon-button type="button" (click)="sync()" [disabled]="!state.online || state.syncing" [matTooltip]="'offline.sync_now' | translate">
        <mat-icon>sync</mat-icon>
      </button>
      <div class="offline-sync__conflicts" *ngIf="state.conflicts.length > 0">
        <div *ngFor="let conflict of state.conflicts">
          <strong>{{ 'offline.conflict' | translate }}</strong>
          <span>{{ conflict.blocking_reason }}</span>
        </div>
      </div>
    </section>
  `,
  styles: [`
    .offline-sync { display: grid; grid-template-columns: 1fr auto; gap: 8px; align-items: center; margin-bottom: 12px; padding: 8px 12px; border: 1px solid rgba(46, 125, 50, .35); border-radius: 6px; background: #f1f8f4; color: #1b5e20; font-size: 13px; }
    .offline-sync.offline { border-color: rgba(245, 124, 0, .35); background: #fff8e1; color: #e65100; }
    .offline-sync.has-conflict { border-color: rgba(198, 40, 40, .35); background: #ffebee; color: #b71c1c; }
    .offline-sync__main { display: flex; min-width: 0; align-items: center; gap: 8px; flex-wrap: wrap; }
    .offline-sync__count { font-weight: 600; }
    .offline-sync__conflicts { grid-column: 1 / -1; display: grid; gap: 4px; }
    .offline-sync__conflicts div { display: flex; gap: 6px; flex-wrap: wrap; }
  `],
})
export class OfflineSyncPanelComponent {
  state$: Observable<OfflineSyncState> = this.offlineSync.state$;

  constructor(private offlineSync: OfflineSyncService) {}

  sync(): void {
    this.offlineSync.syncPending();
  }
}
