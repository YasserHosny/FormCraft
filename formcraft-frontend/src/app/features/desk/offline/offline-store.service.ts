import { Injectable } from '@angular/core';
import { EncryptedOfflinePayload, OfflineCryptoService } from './offline-crypto.service';

export interface OfflineQueueItem {
  idempotencyKey: string;
  templateId: string;
  templateVersion: number;
  operationType: 'draft' | 'submission';
  createdAt: string;
  status: 'pending' | 'syncing' | 'submitted' | 'failed' | 'conflict';
  payloadDigest: string;
  encryptedPayload: EncryptedOfflinePayload;
}

@Injectable({ providedIn: 'root' })
export class OfflineStoreService {
  private dbPromise: Promise<IDBDatabase> | null = null;

  constructor(private offlineCrypto: OfflineCryptoService) {}

  saveDraft(templateId: string, templateVersion: number, values: Record<string, unknown>): Promise<OfflineQueueItem> {
    return this.putItem('draft', templateId, templateVersion, values);
  }

  queueSubmission(templateId: string, templateVersion: number, values: Record<string, unknown>): Promise<OfflineQueueItem> {
    return this.putItem('submission', templateId, templateVersion, values);
  }

  async listQueue(): Promise<OfflineQueueItem[]> {
    const db = await this.openDb();
    return new Promise((resolve, reject) => {
      const request = db.transaction('queue', 'readonly').objectStore('queue').getAll();
      request.onsuccess = () => resolve(request.result as OfflineQueueItem[]);
      request.onerror = () => reject(request.error);
    });
  }

  async markStatus(idempotencyKey: string, status: OfflineQueueItem['status']): Promise<void> {
    const db = await this.openDb();
    const items = await this.listQueue();
    const item = items.find((entry) => entry.idempotencyKey === idempotencyKey);
    if (item) await this.write(db, { ...item, status });
  }

  async remove(idempotencyKey: string): Promise<void> {
    const db = await this.openDb();
    return new Promise((resolve, reject) => {
      const request = db.transaction('queue', 'readwrite').objectStore('queue').delete(idempotencyKey);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  private async putItem(operationType: 'draft' | 'submission', templateId: string, templateVersion: number, values: Record<string, unknown>): Promise<OfflineQueueItem> {
    const db = await this.openDb();
    const item: OfflineQueueItem = {
      idempotencyKey: crypto.randomUUID(),
      templateId,
      templateVersion,
      operationType,
      createdAt: new Date().toISOString(),
      status: 'pending',
      payloadDigest: await this.offlineCrypto.digest(values),
      encryptedPayload: await this.offlineCrypto.encrypt(values),
    };
    await this.write(db, item);
    return item;
  }

  private write(db: IDBDatabase, item: OfflineQueueItem): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = db.transaction('queue', 'readwrite').objectStore('queue').put(item);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  private openDb(): Promise<IDBDatabase> {
    this.dbPromise ??= new Promise((resolve, reject) => {
      const request = indexedDB.open('formcraft-offline-desk', 1);
      request.onupgradeneeded = () => request.result.createObjectStore('queue', { keyPath: 'idempotencyKey' });
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    return this.dbPromise;
  }
}
