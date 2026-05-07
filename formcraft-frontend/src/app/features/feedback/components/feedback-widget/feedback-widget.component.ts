import { Component, ElementRef, OnDestroy, ViewChild } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { AuthService } from '../../../../core/auth/auth.service';
import { FeedbackService, FeedbackSubmitRequest } from '../../services/feedback.service';
import { AudioRecorderService, RecordingState } from '../../services/audio-recorder.service';

@Component({
  selector: 'fc-feedback-widget',
  standalone: false,
  templateUrl: './feedback-widget.component.html',
  styleUrls: ['./feedback-widget.component.scss'],
})
export class FeedbackWidgetComponent implements OnDestroy {
  isModalOpen = false;
  isSubmitting = false;
  isSuccess = false;
  errorMessage: string | null = null;
  cooldownRemaining = 0;
  isOnline = true;

  textControl = new FormControl('', { updateOn: 'change' });
  charCount = 0;
  readonly maxChars = 2000;

  imageUrl: string | null = null;
  imagePreviewUrl: string | null = null;
  imageValidationError: string | null = null;
  isUploadingImage = false;
  readonly MAX_IMAGE_SIZE = 5 * 1024 * 1024;
  readonly ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

  audioUrl: string | null = null;
  audioValidationError: string | null = null;
  isUploadingAudio = false;
  isAudioRecording = false;
  audioElapsedSeconds = 0;
  readonly MAX_AUDIO_SIZE = 10 * 1024 * 1024;
  readonly MAX_AUDIO_SECONDS = 120;
  readonly ALLOWED_AUDIO_TYPES = ['audio/mpeg', 'audio/mp4', 'audio/wav', 'audio/webm', 'audio/x-m4a'];
  audioPreviewUrl: string | null = null;
  hasAudioPreview = false;
  get isAudioSupported(): boolean {
    return this.audioRecorder.state$.value?.isSupported ?? false;
  }

  @ViewChild('imageInput') imageInput!: ElementRef<HTMLInputElement>;
  @ViewChild('audioInput') audioInput!: ElementRef<HTMLInputElement>;

  private destroy$ = new Subject<void>();
  private cooldownTimer: ReturnType<typeof setInterval> | null = null;
  private lastSubmitTime = 0;
  private readonly SUBMIT_DEBOUNCE_MS = 300;

  constructor(
    private feedbackService: FeedbackService,
    private authService: AuthService,
    private audioRecorder: AudioRecorderService,
  ) {
    this.textControl.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe((val) => {
        this.charCount = (val || '').length;
      });

    this.audioRecorder.state$.pipe(takeUntil(this.destroy$)).subscribe((state: RecordingState) => {
      this.isAudioRecording = state.isRecording;
      this.audioElapsedSeconds = state.elapsedSeconds;
      if (state.blob && !state.isRecording && !this.audioUrl) {
        this.handleRecordedAudio(state.blob);
      }
      if (state.error && state.error !== 'feedback.microphoneDenied') {
        this.audioValidationError = state.error;
      }
    });

    this.isOnline = navigator.onLine;
    window.addEventListener('online', () => { this.isOnline = true; });
    window.addEventListener('offline', () => { this.isOnline = false; });
  }

  get isAuthenticated(): boolean {
    return this.authService.isAuthenticated$.value ?? false;
  }

  get canSubmit(): boolean {
    const text = (this.textControl.value || '').trim();
    return text.length > 0 && text.length <= this.maxChars && !this.isSubmitting && !this.isUploadingImage && !this.isUploadingAudio && this.cooldownRemaining === 0 && this.isOnline;
  }

  openModal(): void {
    this.isModalOpen = true;
    this.isSuccess = false;
    this.errorMessage = null;
  }

  closeModal(): void {
    this.isModalOpen = false;
    this.resetForm();
  }

  onSubmit(): void {
    if (!this.canSubmit) return;
    const now = Date.now();
    if (now - this.lastSubmitTime < this.SUBMIT_DEBOUNCE_MS) return;
    this.lastSubmitTime = now;

    const text = (this.textControl.value || '').trim();
    if (!text) return;

    if (!this.isOnline) {
      this.errorMessage = 'You appear to be offline — please check your connection and try again.';
      return;
    }

    this.isSubmitting = true;
    this.errorMessage = null;

    const payload: FeedbackSubmitRequest = {
      page_url: window.location.href,
      text_content: text,
      image_url: this.imageUrl,
      audio_url: this.audioUrl,
    };

    this.feedbackService.submitFeedback(payload).subscribe({
      next: () => {
        this.isSuccess = true;
        this.isSubmitting = false;
      },
      error: (err) => {
        this.isSubmitting = false;
        if (err.status === 429) {
          const match = err.error?.detail?.match(/(\d+)/);
          const seconds = match ? parseInt(match[1], 10) : 30;
          this.startCooldown(seconds);
          this.errorMessage = `Please wait ${seconds} seconds before submitting again.`;
        } else {
          this.errorMessage = 'Something went wrong. Please try again.';
          if (this.audioUrl) {
            this.feedbackService.deleteUpload(this.audioUrl).subscribe();
          }
          if (this.imageUrl) {
            this.feedbackService.deleteUpload(this.imageUrl).subscribe();
          }
        }
      },
    });
  }

  onImageSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.imageValidationError = null;

    if (!this.ALLOWED_IMAGE_TYPES.includes(file.type)) {
      this.imageValidationError = 'feedback.invalidImageType';
      input.value = '';
      return;
    }

    if (file.size > this.MAX_IMAGE_SIZE) {
      this.imageValidationError = 'feedback.imageTooLarge';
      input.value = '';
      return;
    }

    this.isUploadingImage = true;
    this.imagePreviewUrl = URL.createObjectURL(file);

    this.feedbackService.uploadImage(file).subscribe({
      next: (res) => {
        this.imageUrl = res.url;
        this.isUploadingImage = false;
      },
      error: () => {
        this.feedbackService.uploadImage(file).subscribe({
          next: (retryRes) => {
            this.imageUrl = retryRes.url;
            this.isUploadingImage = false;
          },
          error: () => {
            this.isUploadingImage = false;
            this.imageValidationError = 'feedback.imageUploadFailed';
          },
        });
      },
    });
  }

  removeImage(): void {
    if (this.imagePreviewUrl) {
      URL.revokeObjectURL(this.imagePreviewUrl);
    }
    this.imageUrl = null;
    this.imagePreviewUrl = null;
    this.imageValidationError = null;
    this.isUploadingImage = false;
    if (this.imageInput) {
      this.imageInput.nativeElement.value = '';
    }
  }

  startAudioRecording(): void {
    this.audioValidationError = null;
    this.audioRecorder.startRecording();
  }

  stopAudioRecording(): void {
    this.audioRecorder.stopRecording();
  }

  private handleRecordedAudio(blob: Blob): void {
    this.isUploadingAudio = true;
    this.audioPreviewUrl = URL.createObjectURL(blob);
    this.hasAudioPreview = true;

    this.feedbackService.uploadAudio(blob).subscribe({
      next: (res) => {
        this.audioUrl = res.url;
        this.isUploadingAudio = false;
      },
      error: () => {
        this.feedbackService.uploadAudio(blob).subscribe({
          next: (retryRes) => {
            this.audioUrl = retryRes.url;
            this.isUploadingAudio = false;
          },
          error: () => {
            this.isUploadingAudio = false;
            this.audioValidationError = 'feedback.audioUploadFailed';
            this.hasAudioPreview = false;
            if (this.audioPreviewUrl) {
              URL.revokeObjectURL(this.audioPreviewUrl);
              this.audioPreviewUrl = null;
            }
          },
        });
      },
    });
  }

  onAudioFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.audioValidationError = null;

    if (!this.ALLOWED_AUDIO_TYPES.includes(file.type) && !file.name.match(/\.(mp3|m4a|wav|webm)$/i)) {
      this.audioValidationError = 'feedback.invalidAudioType';
      input.value = '';
      return;
    }

    if (file.size > this.MAX_AUDIO_SIZE) {
      this.audioValidationError = 'feedback.audioTooLarge';
      input.value = '';
      return;
    }

    this.isUploadingAudio = true;
    this.audioPreviewUrl = URL.createObjectURL(file);
    this.hasAudioPreview = true;

    this.feedbackService.uploadAudio(file).subscribe({
      next: (res) => {
        this.audioUrl = res.url;
        this.isUploadingAudio = false;
      },
      error: () => {
        this.feedbackService.uploadAudio(file).subscribe({
          next: (retryRes) => {
            this.audioUrl = retryRes.url;
            this.isUploadingAudio = false;
          },
          error: () => {
            this.isUploadingAudio = false;
            this.audioValidationError = 'feedback.audioUploadFailed';
            this.hasAudioPreview = false;
            if (this.audioPreviewUrl) {
              URL.revokeObjectURL(this.audioPreviewUrl);
              this.audioPreviewUrl = null;
            }
          },
        });
      },
    });
  }

  rerecordAudio(): void {
    this.removeAudio();
    this.startAudioRecording();
  }

  removeAudio(): void {
    if (this.audioPreviewUrl) {
      URL.revokeObjectURL(this.audioPreviewUrl);
    }
    this.audioUrl = null;
    this.audioPreviewUrl = null;
    this.audioValidationError = null;
    this.isUploadingAudio = false;
    this.hasAudioPreview = false;
    this.audioRecorder.reset();
    if (this.audioInput) {
      this.audioInput.nativeElement.value = '';
    }
  }

  private startCooldown(seconds: number): void {
    this.cooldownRemaining = seconds;
    if (this.cooldownTimer) clearInterval(this.cooldownTimer);
    this.cooldownTimer = setInterval(() => {
      this.cooldownRemaining--;
      if (this.cooldownRemaining <= 0) {
        this.cooldownRemaining = 0;
        if (this.cooldownTimer) clearInterval(this.cooldownTimer);
        this.cooldownTimer = null;
        this.errorMessage = null;
      }
    }, 1000);
  }

  private resetForm(): void {
    this.textControl.reset('');
    this.charCount = 0;
    this.isSuccess = false;
    this.errorMessage = null;
    this.isSubmitting = false;
    this.cooldownRemaining = 0;
    this.imageUrl = null;
    this.imageValidationError = null;
    this.isUploadingImage = false;
    if (this.imagePreviewUrl) {
      URL.revokeObjectURL(this.imagePreviewUrl);
    }
    this.imagePreviewUrl = null;
    this.audioUrl = null;
    this.audioValidationError = null;
    this.isUploadingAudio = false;
    this.hasAudioPreview = false;
    if (this.audioPreviewUrl) {
      URL.revokeObjectURL(this.audioPreviewUrl);
    }
    this.audioPreviewUrl = null;
    this.audioRecorder.reset();
    if (this.cooldownTimer) {
      clearInterval(this.cooldownTimer);
      this.cooldownTimer = null;
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.cooldownTimer) clearInterval(this.cooldownTimer);
  }
}