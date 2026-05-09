import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';

export interface RecordingState {
  isRecording: boolean;
  isSupported: boolean;
  elapsedSeconds: number;
  maxSeconds: number;
  blob: Blob | null;
  previewUrl: SafeUrl | null;
  error: string | null;
}

@Injectable({ providedIn: 'root' })
export class AudioRecorderService {
  private stateSubject = new BehaviorSubject<RecordingState>({
    isRecording: false,
    isSupported: false,
    elapsedSeconds: 0,
    maxSeconds: 120,
    blob: null,
    previewUrl: null,
    error: null,
  });

  // Expose BehaviorSubject so callers can read .value synchronously.
  state$ = this.stateSubject;

  private mediaRecorder: MediaRecorder | null = null;
  private chunks: Blob[] = [];
  private timer: ReturnType<typeof setInterval> | null = null;

  constructor(private sanitizer: DomSanitizer) {
    this.checkBrowserSupport();
  }

  private checkBrowserSupport(): void {
    const supported =
      typeof navigator !== 'undefined' &&
      !!navigator.mediaDevices &&
      !!navigator.mediaDevices.getUserMedia &&
      typeof MediaRecorder !== 'undefined';
    this.stateSubject.next({ ...this.stateSubject.value, isSupported: supported });
  }

  startRecording(): void {
    if (!this.stateSubject.value.isSupported || this.stateSubject.value.isRecording) {
      return;
    }

    this.cleanup();

    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        const options: MediaRecorderOptions = {};
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
          options.mimeType = 'audio/webm;codecs=opus';
        }

        this.mediaRecorder = new MediaRecorder(stream, options);
        this.chunks = [];

        this.mediaRecorder.ondataavailable = (event: BlobEvent) => {
          if (event.data.size > 0) {
            this.chunks.push(event.data);
          }
        };

        this.mediaRecorder.onstop = () => {
          const blob = new Blob(this.chunks, {
            type: this.mediaRecorder?.mimeType || 'audio/webm',
          });
          const url = this.sanitizer.bypassSecurityTrustUrl(URL.createObjectURL(blob));
          this.stateSubject.next({
            ...this.stateSubject.value,
            isRecording: false,
            blob,
            previewUrl: url,
          });
          stream.getTracks().forEach((t) => t.stop());
        };

        this.mediaRecorder.onerror = () => {
          this.stateSubject.next({
            ...this.stateSubject.value,
            isRecording: false,
            error: 'Microphone error occurred',
          });
          stream.getTracks().forEach((t) => t.stop());
        };

        this.mediaRecorder.start(1000);

        this.stateSubject.next({
          ...this.stateSubject.value,
          isRecording: true,
          elapsedSeconds: 0,
          blob: null,
          previewUrl: null,
          error: null,
        });

        this.startTimer();
      })
      .catch((err) => {
        let errorMsg = 'Microphone access denied';
        if (err.name === 'NotAllowedError') {
          errorMsg = 'feedback.microphoneDenied';
        } else if (err.name === 'NotFoundError') {
          errorMsg = 'feedback.microphoneNotFound';
        }
        this.stateSubject.next({
          ...this.stateSubject.value,
          isRecording: false,
          error: errorMsg,
        });
      });
  }

  stopRecording(): void {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
    }
    this.stopTimer();
  }

  reset(): void {
    this.cleanup();
    this.stateSubject.next({
      isRecording: false,
      isSupported: this.stateSubject.value.isSupported,
      elapsedSeconds: 0,
      maxSeconds: 120,
      blob: null,
      previewUrl: null,
      error: null,
    });
  }

  private startTimer(): void {
    this.stopTimer();
    this.timer = setInterval(() => {
      const current = this.stateSubject.value;
      const newElapsed = current.elapsedSeconds + 1;
      if (newElapsed >= current.maxSeconds) {
        this.stopRecording();
        return;
      }
      this.stateSubject.next({ ...current, elapsedSeconds: newElapsed });
    }, 1000);
  }

  private stopTimer(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  private cleanup(): void {
    this.stopTimer();
    if (this.stateSubject.value.previewUrl) {
      const url = this.stateSubject.value.previewUrl as string;
      if (url) {
        URL.revokeObjectURL(url);
      }
    }
    this.chunks = [];
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
    }
    this.mediaRecorder = null;
  }
}