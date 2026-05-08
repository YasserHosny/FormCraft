import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Subject } from 'rxjs';

export interface VideoRecordingResult {
  blob: Blob;
  objectUrl: string;
}

@Injectable({ providedIn: 'root' })
export class VideoRecorderService {
  private canRecordSubject = new BehaviorSubject<boolean>(false);
  canRecord$: Observable<boolean> = this.canRecordSubject.asObservable();

  permissionError$ = new Subject<void>();

  private elapsedSecondsSubject = new BehaviorSubject<number>(0);
  elapsedSeconds$: Observable<number> = this.elapsedSecondsSubject.asObservable();

  private recordingBlobSubject = new BehaviorSubject<VideoRecordingResult | null>(null);
  recordingBlob$: Observable<VideoRecordingResult | null> = this.recordingBlobSubject.asObservable();

  private isRecordingSubject = new BehaviorSubject<boolean>(false);
  isRecording$: Observable<boolean> = this.isRecordingSubject.asObservable();

  private mediaRecorder: MediaRecorder | null = null;
  private chunks: Blob[] = [];
  private stream: MediaStream | null = null;
  private timer: ReturnType<typeof setInterval> | null = null;
  private readonly maxSeconds = 120;

  constructor() {
    this.checkSupport();
  }

  private checkSupport(): void {
    const supported =
      typeof navigator !== 'undefined' &&
      !!navigator.mediaDevices &&
      !!navigator.mediaDevices.getUserMedia &&
      typeof MediaRecorder !== 'undefined' &&
      MediaRecorder.isTypeSupported('video/webm;codecs=vp8');
    this.canRecordSubject.next(supported);
  }

  start(): void {
    if (!this.canRecordSubject.value || this.isRecordingSubject.value) {
      return;
    }

    this.cleanup();

    navigator.mediaDevices
      .getUserMedia({ video: true, audio: true })
      .then((stream) => {
        this.stream = stream;
        const options: MediaRecorderOptions = {};
        if (MediaRecorder.isTypeSupported('video/webm;codecs=vp8')) {
          options.mimeType = 'video/webm;codecs=vp8';
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
            type: this.mediaRecorder?.mimeType || 'video/webm',
          });
          const objectUrl = URL.createObjectURL(blob);
          this.recordingBlobSubject.next({ blob, objectUrl });
          this.isRecordingSubject.next(false);
          this.stopTimer();
          stream.getTracks().forEach((t) => t.stop());
        };

        this.mediaRecorder.onerror = () => {
          this.isRecordingSubject.next(false);
          this.stopTimer();
          stream.getTracks().forEach((t) => t.stop());
        };

        this.mediaRecorder.start(1000);
        this.isRecordingSubject.next(true);
        this.elapsedSecondsSubject.next(0);
        this.startTimer();
      })
      .catch(() => {
        this.permissionError$.next();
        this.isRecordingSubject.next(false);
      });
  }

  stop(): void {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
    } else {
      this.stopTimer();
      this.isRecordingSubject.next(false);
    }
  }

  cleanup(): void {
    this.stopTimer();
    const current = this.recordingBlobSubject.value;
    if (current?.objectUrl) {
      URL.revokeObjectURL(current.objectUrl);
    }
    this.recordingBlobSubject.next(null);
    this.elapsedSecondsSubject.next(0);
    this.chunks = [];
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
    }
    this.mediaRecorder = null;
    if (this.stream) {
      this.stream.getTracks().forEach((t) => t.stop());
      this.stream = null;
    }
  }

  private startTimer(): void {
    this.stopTimer();
    this.timer = setInterval(() => {
      const current = this.elapsedSecondsSubject.value + 1;
      if (current >= this.maxSeconds) {
        this.stop();
        return;
      }
      this.elapsedSecondsSubject.next(current);
    }, 1000);
  }

  private stopTimer(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}
