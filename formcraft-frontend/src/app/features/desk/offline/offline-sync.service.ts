import { Injectable, NgZone } from '@angular/core';
import { BehaviorSubject, firstValueFrom } from 'rxjs';
import { OfflineDeskService, SyncConflict } from '../../../core/services/offline-desk.service';
import { OfflineQueueItem, OfflineStoreService } from './offline-store.service';

export interface OfflineSyncState {
  online: boolean;
  pending: number;
  syncing: boolean;
  conflicts: SyncConflict[];
  lastError: string | null;
}

@Injectable({ providedIn: 'root' })
export class OfflineSyncService {
  private readonly stateSubject = new BehaviorSubject<OfflineSyncState>({
    online: typeof navigator === 'undefined' ? true : navigator.onLine,
    pending: 0,
    syncing: false,
    conflicts: [],
    lastError: null,
  });

  readonly state$ = this.stateSubject.asObservable();

  constructor(
    private offlineStore: OfflineStoreService,
    private offlineDesk: OfflineDeskService,
    private zone: NgZone,
  ) {
    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => this.zone.run(() => this.syncPending()));
      window.addEventListener('offline', () => this.patch({ online: false }));
    }
    this.refreshPending();
  }

  async saveDraft(templateId: string, templateVersion: number, values: Record<string, unknown>): Promise<OfflineQueueItem> {
    const item = await this.offlineStore.saveDraft(templateId, templateVersion, values);
    await this.refreshPending();
    return item;
  }

  async queueSubmission(templateId: string, templateVersion: number, values: Record<string, unknown>): Promise<OfflineQueueItem> {
    const item = await this.offlineStore.queueSubmission(templateId, templateVersion, values);
    await this.refreshPending();
    return item;
  }

  async syncPending(deviceId = localStorage.getItem('formcraft.offlineDeviceId') || ''): Promise<void> {
    if (!deviceId || !navigator.onLine) {
      this.patch({ online: navigator.onLine, syncing: false });
      return;
    }
    this.patch({ online: true, syncing: true, lastError: null });
    try {
      await this.syncItems(deviceId, (await this.offlineStore.listQueue()).filter((item) => item.status !== 'submitted'));
      await this.refreshPending();
    } catch (error: any) {
      this.patch({ syncing: false, lastError: error?.message || 'sync_failed' });
    }
  }

  private async syncItems(deviceId: string, items: OfflineQueueItem[]): Promise<void> {
    const conflicts: SyncConflict[] = [];
    for (const item of items) {
      await this.offlineStore.markStatus(item.idempotencyKey, 'syncing');
      const response = await firstValueFrom(this.offlineDesk.sync({
        device_id: deviceId,
        idempotency_key: item.idempotencyKey,
        operation_type: item.operationType,
        template_id: item.templateId,
        template_version: item.templateVersion,
        payload_digest: item.payloadDigest,
        client_created_at: item.createdAt,
        encrypted_payload: item.encryptedPayload.ciphertext,
      }));
      if (response.status === 'submitted') await this.offlineStore.remove(item.idempotencyKey);
      else if (response.status === 'conflict') {
        await this.offlineStore.markStatus(item.idempotencyKey, 'conflict');
        conflicts.push(...response.conflicts);
      } else {
        await this.offlineStore.markStatus(item.idempotencyKey, 'failed');
      }
    }
    this.patch({ syncing: false, conflicts, lastError: null });
  }

  private async refreshPending(): Promise<void> {
    const queue = await this.offlineStore.listQueue().catch(() => []);
    this.patch({ online: typeof navigator === 'undefined' ? true : navigator.onLine, pending: queue.filter((item) => item.status !== 'submitted').length });
  }

  private patch(partial: Partial<OfflineSyncState>): void {
    this.stateSubject.next({ ...this.stateSubject.value, ...partial });
  }
}
