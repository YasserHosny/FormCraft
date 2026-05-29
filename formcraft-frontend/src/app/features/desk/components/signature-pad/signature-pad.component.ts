import { Component, Input, Output, EventEmitter, ViewChild, ElementRef, AfterViewInit, OnDestroy, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'fc-signature-pad',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatFormFieldModule, MatIconModule, TranslateModule],
  template: `
    <div class="signature-pad-container">
      <label class="signature-label" *ngIf="label">{{ label }}</label>
      <div class="canvas-wrapper" #canvasWrapper>
        <canvas #signatureCanvas
          (mousedown)="onMouseDown($event)"
          (mousemove)="onMouseMove($event)"
          (mouseup)="onMouseUp()"
          (mouseleave)="onMouseUp()"
          (touchstart)="onTouchStart($event)"
          (touchmove)="onTouchMove($event)"
          (touchend)="onMouseUp()">
        </canvas>
      </div>
      <div class="signature-actions">
        <button mat-stroked-button (click)="clear()" [disabled]="isEmpty">
          <mat-icon>delete_outline</mat-icon>
          {{ 'signature.clear' | translate }}
        </button>
        <button mat-raised-button color="primary" (click)="confirm()" [disabled]="isEmpty">
          <mat-icon>check</mat-icon>
          {{ 'signature.confirm' | translate }}
        </button>
      </div>
      <mat-error *ngIf="required && isEmpty && touched" class="signature-error">
        {{ 'signature.required' | translate }}
      </mat-error>
    </div>
  `,
  styles: [`
    .signature-pad-container {
      display: flex;
      flex-direction: column;
      gap: 8px;
      width: 100%;
    }
    .signature-label {
      font-size: 14px;
      color: rgba(0,0,0,0.87);
      margin-bottom: 4px;
    }
    .canvas-wrapper {
      border: 2px dashed #999;
      border-radius: 4px;
      background: #fafafa;
      overflow: hidden;
      touch-action: none;
    }
    canvas {
      display: block;
      width: 100%;
      cursor: crosshair;
    }
    .signature-actions {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
    }
    .signature-actions button mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
      margin-right: 4px;
    }
    .signature-error {
      font-size: 12px;
    }
    :host-context([dir='rtl']) .signature-label {
      text-align: right;
    }
  `],
})
export class SignaturePadComponent implements AfterViewInit, OnDestroy, OnChanges {
  @Input() label = '';
  @Input() penColor = '#000000';
  @Input() required = false;
  @Input() value: string | null = null;
  @Output() valueChange = new EventEmitter<string>();

  @ViewChild('signatureCanvas', { static: true }) canvasRef!: ElementRef<HTMLCanvasElement>;

  isEmpty = true;
  touched = false;

  private ctx: CanvasRenderingContext2D | null = null;
  private drawing = false;
  private lastPoint: { x: number; y: number } | null = null;
  private resizeObserver: ResizeObserver | null = null;

  ngAfterViewInit(): void {
    this.initCanvas();
    this.resizeObserver = new ResizeObserver(() => this.resizeCanvas());
    this.resizeObserver.observe(this.canvasRef.nativeElement.parentElement!);
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['value'] && !changes['value'].firstChange) {
      if (!changes['value'].currentValue) {
        this.clear();
      }
    }
  }

  ngOnDestroy(): void {
    this.resizeObserver?.disconnect();
  }

  private initCanvas(): void {
    const canvas = this.canvasRef.nativeElement;
    const wrapper = canvas.parentElement!;
    canvas.width = wrapper.clientWidth;
    canvas.height = Math.max(wrapper.clientWidth * 0.4, 100);
    this.ctx = canvas.getContext('2d');
    this.ctx!.lineWidth = 2;
    this.ctx!.lineCap = 'round';
    this.ctx!.lineJoin = 'round';
    this.ctx!.strokeStyle = this.penColor;
    this.isEmpty = true;
  }

  private resizeCanvas(): void {
    if (!this.canvasRef?.nativeElement) return;
    const canvas = this.canvasRef.nativeElement;
    const wrapper = canvas.parentElement!;
    const dataUrl = this.isEmpty ? null : canvas.toDataURL('image/png');
    canvas.width = wrapper.clientWidth;
    canvas.height = Math.max(wrapper.clientWidth * 0.4, 100);
    this.ctx = canvas.getContext('2d');
    this.ctx!.lineWidth = 2;
    this.ctx!.lineCap = 'round';
    this.ctx!.lineJoin = 'round';
    this.ctx!.strokeStyle = this.penColor;
    if (dataUrl) {
      const img = new Image();
      img.onload = () => {
        this.ctx!.drawImage(img, 0, 0);
      };
      img.src = dataUrl;
    }
  }

  onMouseDown(event: MouseEvent): void {
    event.preventDefault();
    this.drawing = true;
    this.touched = true;
    const point = this.getPoint(event);
    this.lastPoint = point;
    this.ctx!.beginPath();
    this.ctx!.moveTo(point.x, point.y);
  }

  onMouseMove(event: MouseEvent): void {
    if (!this.drawing) return;
    event.preventDefault();
    const point = this.getPoint(event);
    this.ctx!.lineTo(point.x, point.y);
    this.ctx!.stroke();
    this.lastPoint = point;
    this.isEmpty = false;
  }

  onMouseUp(): void {
    this.drawing = false;
    this.lastPoint = null;
  }

  onTouchStart(event: TouchEvent): void {
    event.preventDefault();
    const touch = event.touches[0];
    const canvas = this.canvasRef.nativeElement;
    const rect = canvas.getBoundingClientRect();
    const point = {
      x: touch.clientX - rect.left,
      y: touch.clientY - rect.top,
    };
    this.drawing = true;
    this.touched = true;
    this.lastPoint = point;
    this.ctx!.beginPath();
    this.ctx!.moveTo(point.x, point.y);
  }

  onTouchMove(event: TouchEvent): void {
    if (!this.drawing) return;
    event.preventDefault();
    const touch = event.touches[0];
    const canvas = this.canvasRef.nativeElement;
    const rect = canvas.getBoundingClientRect();
    const point = {
      x: touch.clientX - rect.left,
      y: touch.clientY - rect.top,
    };
    this.ctx!.lineTo(point.x, point.y);
    this.ctx!.stroke();
    this.lastPoint = point;
    this.isEmpty = false;
  }

  clear(): void {
    if (!this.ctx) return;
    const canvas = this.canvasRef.nativeElement;
    this.ctx.clearRect(0, 0, canvas.width, canvas.height);
    this.isEmpty = true;
    this.valueChange.emit('');
  }

  confirm(): void {
    if (this.isEmpty) return;
    const canvas = this.canvasRef.nativeElement;
    const dataUrl = canvas.toDataURL('image/png');
    this.valueChange.emit(dataUrl);
  }

  private getPoint(event: MouseEvent): { x: number; y: number } {
    const canvas = this.canvasRef.nativeElement;
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  }
}
