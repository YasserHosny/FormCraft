import { Injectable } from '@angular/core';

export interface EncryptedOfflinePayload {
  iv: string;
  ciphertext: string;
}

@Injectable({ providedIn: 'root' })
export class OfflineCryptoService {
  private keyPromise: Promise<CryptoKey> | null = null;

  async encrypt(payload: unknown): Promise<EncryptedOfflinePayload> {
    const key = await this.getKey();
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const data = new TextEncoder().encode(JSON.stringify(payload));
    const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, data);
    return { iv: this.toBase64(iv), ciphertext: this.toBase64(new Uint8Array(encrypted)) };
  }

  async decrypt<T>(payload: EncryptedOfflinePayload): Promise<T> {
    const key = await this.getKey();
    const decrypted = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: this.fromBase64(payload.iv) }, key, this.fromBase64(payload.ciphertext));
    return JSON.parse(new TextDecoder().decode(decrypted)) as T;
  }

  async digest(payload: unknown): Promise<string> {
    const data = new TextEncoder().encode(JSON.stringify(payload));
    const digest = await crypto.subtle.digest('SHA-256', data);
    return `sha256:${Array.from(new Uint8Array(digest)).map((byte) => byte.toString(16).padStart(2, '0')).join('')}`;
  }

  private getKey(): Promise<CryptoKey> {
    this.keyPromise ??= crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
    return this.keyPromise;
  }

  private toBase64(bytes: Uint8Array): string {
    return btoa(String.fromCharCode(...bytes));
  }

  private fromBase64(value: string): Uint8Array {
    return Uint8Array.from(atob(value), (char) => char.charCodeAt(0));
  }
}
