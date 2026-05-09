import { Component, ElementRef, OnDestroy, ViewChild } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { AuthService } from '../../../../core/auth/auth.service';
import { FeedbackService, FeedbackSubmitRequest } from '../../services/feedback.service';
import { AudioRecorderService, RecordingState } from '../../services/audio-recorder.service';
import { VideoRecorderService, VideoRecordingResult } from '../../services/video-recorder.service';

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

  stagedImages: { file: File; objectUrl: string; storagePath?: string }[] = [];
  imageValidationError: string | null = null;
  isUploadingImage = false;
  readonly MAX_IMAGES = 5;
  readonly MAX_IMAGE_SIZE = 5 * 1024 * 1024;
  readonly ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

  stagedVideo: { blob?: Blob; file?: File; objectUrl?: string; storagePath?: string } | null = null;
  videoValidationError: string | null = null;
  isUploadingVideo = false;
  isVideoRecording = false;
  videoElapsedSeconds = 0;
  readonly MAX_VIDEO_SIZE = 100 * 1024 * 1024;
  readonly MAX_VIDEO_SECONDS = 120;
  readonly ALLOWED_VIDEO_TYPES = ['video/webm', 'video/mp4', 'video/quicktime'];

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

  get isAudioBlockedByVideo(): boolean {
    return this.stagedVideo !== null;
  }

  get isVideoBlockedByAudio(): boolean {
    return this.audioUrl !== null || this.isAudioRecording;
  }

  get videoCanRecord$() {
    return this.videoRecorder.canRecord$;
  }

  @ViewChild('imageInput') imageInput!: ElementRef<HTMLInputElement>;
  @ViewChild('audioInput') audioInput!: ElementRef<HTMLInputElement>;
  @ViewChild('videoInput') videoInput!: ElementRef<HTMLInputElement>;

  private destroy$ = new Subject<void>();
  private cooldownTimer: ReturnType<typeof setInterval> | null = null;
  private lastSubmitTime = 0;
  private readonly SUBMIT_DEBOUNCE_MS = 300;

  constructor(
    private feedbackService: FeedbackService,
    private authService: AuthService,
    private audioRecorder: AudioRecorderService,
    private videoRecorder: VideoRecorderService,
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

    this.videoRecorder.isRecording$.pipe(takeUntil(this.destroy$)).subscribe((isRecording) => {
      this.isVideoRecording = isRecording;
    });

    this.videoRecorder.elapsedSeconds$.pipe(takeUntil(this.destroy$)).subscribe((seconds) => {
      this.videoElapsedSeconds = seconds;
    });

    this.videoRecorder.recordingBlob$.pipe(takeUntil(this.destroy$)).subscribe((result: VideoRecordingResult | null) => {
      if (result) {
        this.stagedVideo = { blob: result.blob, objectUrl: result.objectUrl };
      }
    });

    this.videoRecorder.permissionError$.pipe(takeUntil(this.destroy$)).subscribe(() => {
      this.videoValidationError = 'feedback.cameraDenied';
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
    return text.length > 0 && text.length <= this.maxChars && !this.isSubmitting && !this.isUploadingImage && !this.isUploadingAudio && !this.isUploadingVideo && this.cooldownRemaining === 0 && this.isOnline;
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

    const imagePaths: string[] = [];
    let uploadIndex = 0;

    const uploadNextImage = () => {
      if (uploadIndex >= this.stagedImages.length) {
        this.uploadVideoAndSubmit(text, imagePaths);
        return;
      }

      const img = this.stagedImages[uploadIndex];
      if (img.storagePath) {
        imagePaths.push(img.storagePath);
        uploadIndex++;
        uploadNextImage();
        return;
      }

      this.isUploadingImage = true;
      this.feedbackService.uploadImage(img.file).subscribe({
        next: (res) => {
          this.stagedImages[uploadIndex].storagePath = res.storage_path;
          imagePaths.push(res.storage_path);
          uploadIndex++;
          uploadNextImage();
        },
        error: () => {
          this.isUploadingImage = false;
          this.isSubmitting = false;
          this.imageValidationError = 'feedback.imageUploadFailed';
          imagePaths.forEach((path) => {
            this.feedbackService.deleteUpload('image', path).subscribe();
          });
        },
      });
    };

    uploadNextImage();
  }

  private uploadVideoAndSubmit(text: string, imagePaths: string[]): void {
    if (this.stagedVideo && !this.stagedVideo.storagePath) {
      this.isUploadingVideo = true;
      const videoFile = this.stagedVideo.file || new File([this.stagedVideo.blob!], 'video.webm', { type: 'video/webm' });
      this.feedbackService.uploadVideo(videoFile).subscribe({
        next: (res) => {
          this.stagedVideo!.storagePath = res.storage_path;
          this.doSubmit(text, imagePaths, res.storage_path);
        },
        error: () => {
          this.isUploadingVideo = false;
          this.isSubmitting = false;
          this.videoValidationError = 'feedback.videoUploadFailed';
          imagePaths.forEach((path) => {
            this.feedbackService.deleteUpload('image', path).subscribe();
          });
        },
      });
    } else {
      this.doSubmit(text, imagePaths, this.stagedVideo?.storagePath || null);
    }
  }

  private doSubmit(text: string, imagePaths: string[], videoUrl: string | null): void {
    const payload: FeedbackSubmitRequest = {
      page_url: window.location.href,
      text_content: text,
      image_paths: imagePaths.length > 0 ? imagePaths : null,
      audio_url: this.audioUrl,
      video_url: videoUrl,
    };

    this.feedbackService.submitFeedback(payload).subscribe({
      next: () => {
        this.isSuccess = true;
        this.isSubmitting = false;
        this.isUploadingImage = false;
        this.isUploadingVideo = false;
      },
      error: (err) => {
        this.isSubmitting = false;
        this.isUploadingImage = false;
        this.isUploadingVideo = false;
        if (err.status === 429) {
          const match = err.error?.detail?.match(/(\d+)/);
          const seconds = match ? parseInt(match[1], 10) : 30;
          this.startCooldown(seconds);
          this.errorMessage = `Please wait ${seconds} seconds before submitting again.`;
        } else {
          this.errorMessage = 'Something went wrong. Please try again.';
          if (this.audioUrl) {
            this.feedbackService.deleteUpload('audio', this.audioUrl).subscribe();
          }
          imagePaths.forEach((path) => {
            this.feedbackService.deleteUpload('image', path).subscribe();
          });
          if (videoUrl) {
            this.feedbackService.deleteUpload('video', videoUrl).subscribe();
          }
        }
      },
    });
  }

  addImage(file: File): void {
    this.imageValidationError = null;

    if (!this.ALLOWED_IMAGE_TYPES.includes(file.type)) {
      this.imageValidationError = 'feedback.invalidImageType';
      return;
    }

    if (file.size > this.MAX_IMAGE_SIZE) {
      this.imageValidationError = 'feedback.imageTooLarge';
      return;
    }

    if (this.stagedImages.length >= this.MAX_IMAGES) {
      this.imageValidationError = 'feedback.maxImagesReached';
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    this.stagedImages.push({ file, objectUrl });
  }

  removeImage(index: number): void {
    const img = this.stagedImages[index];
    if (img.objectUrl) {
      URL.revokeObjectURL(img.objectUrl);
    }
    if (img.storagePath) {
      this.feedbackService.deleteUpload('image', img.storagePath).subscribe();
    }
    this.stagedImages.splice(index, 1);
  }

  onImagesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const files = input.files;
    if (!files) return;
    for (let i = 0; i < files.length; i++) {
      if (this.stagedImages.length >= this.MAX_IMAGES) break;
      this.addImage(files[i]);
    }
    input.value = '';
  }

  startRecording(): void {
    this.videoValidationError = null;
    this.videoRecorder.start();
  }

  stopRecording(): void {
    this.videoRecorder.stop();
  }

  reRecord(): void {
    this.removeVideo();
    this.startRecording();
  }

  attachVideoFile(file: File): void {
    this.videoValidationError = null;

    if (!this.ALLOWED_VIDEO_TYPES.includes(file.type)) {
      this.videoValidationError = 'feedback.invalidVideoType';
      return;
    }

    if (file.size > this.MAX_VIDEO_SIZE) {
      this.videoValidationError = 'feedback.videoTooLarge';
      return;
    }

    this.removeVideo();
    const objectUrl = URL.createObjectURL(file);
    this.stagedVideo = { file, objectUrl };
  }

  onVideoFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    this.attachVideoFile(file);
    input.value = '';
  }

  removeVideo(): void {
    if (this.stagedVideo?.objectUrl) {
      URL.revokeObjectURL(this.stagedVideo.objectUrl);
    }
    if (this.stagedVideo?.storagePath) {
      this.feedbackService.deleteUpload('video', this.stagedVideo.storagePath).subscribe();
    }
    this.stagedVideo = null;
    this.videoValidationError = null;
    this.isUploadingVideo = false;
    this.videoRecorder.cleanup();
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
        this.audioUrl = res.storage_path;
        this.isUploadingAudio = false;
      },
      error: () => {
        this.feedbackService.uploadAudio(blob).subscribe({
          next: (retryRes) => {
            this.audioUrl = retryRes.storage_path;
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
        this.audioUrl = res.storage_path;
        this.isUploadingAudio = false;
      },
      error: () => {
        this.feedbackService.uploadAudio(file).subscribe({
          next: (retryRes) => {
            this.audioUrl = retryRes.storage_path;
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
    if (this.audioUrl) {
      this.feedbackService.deleteUpload('audio', this.audioUrl).subscribe();
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

    this.stagedImages.forEach((img) => {
      if (img.objectUrl) URL.revokeObjectURL(img.objectUrl);
      if (img.storagePath) this.feedbackService.deleteUpload('image', img.storagePath).subscribe();
    });
    this.stagedImages = [];
    this.imageValidationError = null;
    this.isUploadingImage = false;

    this.removeVideo();

    this.removeAudio();

    if (this.cooldownTimer) {
      clearInterval(this.cooldownTimer);
      this.cooldownTimer = null;
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.cooldownTimer) clearInterval(this.cooldownTimer);

    this.stagedImages.forEach((img) => {
      if (img.objectUrl) URL.revokeObjectURL(img.objectUrl);
      if (img.storagePath) this.feedbackService.deleteUpload('image', img.storagePath).subscribe();
    });

    if (this.stagedVideo?.objectUrl) URL.revokeObjectURL(this.stagedVideo.objectUrl);
    if (this.stagedVideo?.storagePath) this.feedbackService.deleteUpload('video', this.stagedVideo.storagePath).subscribe();
    this.videoRecorder.cleanup();

    if (this.audioPreviewUrl) URL.revokeObjectURL(this.audioPreviewUrl);
    if (this.audioUrl) this.feedbackService.deleteUpload('audio', this.audioUrl).subscribe();
    this.audioRecorder.reset();
  }
}
