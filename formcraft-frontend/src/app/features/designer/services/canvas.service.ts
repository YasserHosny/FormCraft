import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';
import Konva from 'konva';
import { mmToPx, pxToMm, snapToGrid, clamp, MIN_ELEMENT_SIZE_MM } from '../models/coordinate-utils';

export interface CanvasElement {
  id: string;
  konvaNode: Konva.Group;
  data: Record<string, unknown>;
}

export interface UndoEntry {
  type: 'add' | 'remove' | 'move' | 'resize' | 'update';
  elementId: string;
  before: Record<string, unknown>;
  after: Record<string, unknown>;
}

@Injectable()
export class CanvasService implements OnDestroy {
  private stage: Konva.Stage | null = null;
  private layer: Konva.Layer | null = null;
  private pageRect: Konva.Rect | null = null;
  private transformer: Konva.Transformer | null = null;
  private detectionLayer: Konva.Layer | null = null;
  private backgroundImage: Konva.Image | null = null;

  private elements = new Map<string, CanvasElement>();
  private undoStack: UndoEntry[] = [];
  private redoStack: UndoEntry[] = [];

  private _selectedElement = new BehaviorSubject<CanvasElement | null>(null);
  selectedElement$ = this._selectedElement.asObservable();

  private _zoom = new BehaviorSubject<number>(1);
  zoom$ = this._zoom.asObservable();

  private _dirty = new BehaviorSubject<boolean>(false);
  dirty$ = this._dirty.asObservable();

  private destroyed$ = new Subject<void>();

  private dpi = 96;
  private gridSizeMm = 2;
  private snapEnabled = true;
  private pageWidthMm = 210;
  private pageHeightMm = 297;
  private detections: { bbox: { x: number; y: number; width: number; height: number }; type?: string }[] = [];

  reset(containerId: string, widthMm: number, heightMm: number): void {
    this.stage?.destroy();
    this.stage = null;
    this.layer = null;
    this.pageRect = null;
    this.transformer = null;
    this.detectionLayer = null;
    this.elements.clear();
    this.undoStack = [];
    this.redoStack = [];
    this._selectedElement.next(null);
    this._dirty.next(false);
    this.detections = [];
    this.init(containerId, widthMm, heightMm);
  }

  init(containerId: string, widthMm: number, heightMm: number): void {
    this.pageWidthMm = widthMm;
    this.pageHeightMm = heightMm;

    const widthPx = mmToPx(widthMm, this.dpi);
    const heightPx = mmToPx(heightMm, this.dpi);

    this.stage = new Konva.Stage({
      container: containerId,
      width: widthPx + 40,
      height: heightPx + 40,
    });

    this.layer = new Konva.Layer();
    this.stage.add(this.layer);

    this.detectionLayer = new Konva.Layer();
    this.stage.add(this.detectionLayer);

    // Page background (white rectangle with shadow)
    this.pageRect = new Konva.Rect({
      x: 20,
      y: 20,
      width: widthPx,
      height: heightPx,
      fill: '#ffffff',
      stroke: '#ccc',
      strokeWidth: 1,
      shadowColor: 'rgba(0,0,0,0.15)',
      shadowBlur: 8,
      shadowOffset: { x: 2, y: 2 },
      listening: false,
    });
    this.layer.add(this.pageRect);

    this.backgroundImage = null;

    // Grid overlay
    this.drawGrid();

    // Transformer for selected elements
    this.transformer = new Konva.Transformer({
      rotateEnabled: false,
      flipEnabled: false,
      boundBoxFunc: (oldBox, newBox) => {
        const minPx = mmToPx(MIN_ELEMENT_SIZE_MM, this.dpi, this._zoom.value);
        if (Math.abs(newBox.width) < minPx || Math.abs(newBox.height) < minPx) {
          return oldBox;
        }
        return newBox;
      },
    });
    this.layer.add(this.transformer);

    // Click on empty space to deselect
    this.stage.on('click tap', (e: Konva.KonvaEventObject<MouseEvent>) => {
      if (e.target === this.stage || e.target === this.pageRect) {
        this.deselectAll();
      }
    });

    this.layer.draw();
    this.detectionLayer.draw();
  }

  setBackgroundImage(imageUrl: string): void {
    if (!this.layer || !this.pageRect) return;
    const img = new window.Image();
    img.onload = () => {
      if (!this.layer || !this.pageRect) return;

      if (this.backgroundImage) {
        this.backgroundImage.destroy();
      }

      this.backgroundImage = new Konva.Image({
        image: img,
        x: this.pageRect.x(),
        y: this.pageRect.y(),
        width: this.pageRect.width(),
        height: this.pageRect.height(),
        listening: false,
      });
      this.layer.add(this.backgroundImage);
      this.backgroundImage.moveToBottom();
      this.pageRect?.moveToBottom();
      this.layer.draw();
    };
    img.src = imageUrl;
  }

  setDetections(detections: { bbox: { x: number; y: number; width: number; height: number }; suggested_type?: string }[]): void {
    this.detections = detections.map((d) => ({ bbox: d.bbox, type: d.suggested_type }));
    this.renderDetections();
  }

  clearDetections(): void {
    this.detections = [];
    this.renderDetections();
  }

  addElement(data: Record<string, unknown>): CanvasElement {
    if (!this.layer) throw new Error('Canvas not initialized');

    const zoom = this._zoom.value;
    const x = mmToPx(data['x_mm'] as number, this.dpi, zoom) + 20;
    const y = mmToPx(data['y_mm'] as number, this.dpi, zoom) + 20;
    const w = mmToPx(data['width_mm'] as number, this.dpi, zoom);
    const h = mmToPx(data['height_mm'] as number, this.dpi, zoom);

    const group = new Konva.Group({ x, y, draggable: true });

    // Element box
    const rect = new Konva.Rect({
      width: w,
      height: h,
      fill: '#f8f9fa',
      stroke: '#90caf9',
      strokeWidth: 1,
      cornerRadius: 2,
    });
    group.add(rect);

    // Label text
    const label = (data['label_ar'] as string) || (data['label_en'] as string) || (data['key'] as string) || '';
    const text = new Konva.Text({
      text: label,
      width: w,
      height: h,
      align: 'center',
      verticalAlign: 'middle',
      fontSize: 12,
      fontFamily: 'Noto Naskh Arabic, Noto Sans, sans-serif',
      fill: '#333',
      listening: false,
    });
    group.add(text);

    // Type badge
    const typeBadge = new Konva.Text({
      text: (data['type'] as string || '').toUpperCase(),
      x: 2,
      y: 2,
      fontSize: 8,
      fontFamily: 'sans-serif',
      fill: '#999',
      listening: false,
    });
    group.add(typeBadge);

    const element: CanvasElement = {
      id: data['id'] as string || `elem_${Date.now()}`,
      konvaNode: group,
      data: { ...data },
    };
    this.elements.set(element.id, element);

    // Click to select
    group.on('click tap', () => this.selectElement(element.id));

    // Drag events with snap
    group.on('dragmove', () => {
      if (this.snapEnabled) {
        const gridPx = mmToPx(this.gridSizeMm, this.dpi, this._zoom.value);
        group.x(snapToGrid(group.x() - 20, gridPx) + 20);
        group.y(snapToGrid(group.y() - 20, gridPx) + 20);
      }
    });

    group.on('dragend', () => {
      const newXMm = pxToMm(group.x() - 20, this.dpi, this._zoom.value);
      const newYMm = pxToMm(group.y() - 20, this.dpi, this._zoom.value);
      this.pushUndo({
        type: 'move',
        elementId: element.id,
        before: { x_mm: element.data['x_mm'], y_mm: element.data['y_mm'] },
        after: { x_mm: newXMm, y_mm: newYMm },
      });
      element.data['x_mm'] = newXMm;
      element.data['y_mm'] = newYMm;
      this._dirty.next(true);
    });

    this.layer.add(group);
    this.transformer!.moveToTop();
    this.layer.draw();
    this._dirty.next(true);

    return element;
  }

  removeElement(id: string): void {
    const el = this.elements.get(id);
    if (!el) return;
    el.konvaNode.destroy();
    this.elements.delete(id);
    if (this._selectedElement.value?.id === id) {
      this.deselectAll();
    }
    this.layer?.draw();
    this._dirty.next(true);
  }

  selectElement(id: string): void {
    const el = this.elements.get(id);
    if (!el || !this.transformer) return;
    this.transformer.nodes([el.konvaNode]);
    this._selectedElement.next(el);
    this.layer?.draw();
  }

  deselectAll(): void {
    this.transformer?.nodes([]);
    this._selectedElement.next(null);
    this.layer?.draw();
  }

  setZoom(zoom: number): void {
    const z = clamp(zoom, 0.25, 3);
    this._zoom.next(z);
    if (this.stage) {
      this.stage.scale({ x: z, y: z });
      this.stage.draw();
    }
    this.renderDetections();
  }

  private renderDetections(): void {
    if (!this.detectionLayer) return;
    this.detectionLayer.destroyChildren();

    const zoom = this._zoom.value;
    for (const detection of this.detections) {
      const x = mmToPx(detection.bbox.x, this.dpi, zoom) + 20;
      const y = mmToPx(detection.bbox.y, this.dpi, zoom) + 20;
      const w = mmToPx(detection.bbox.width, this.dpi, zoom);
      const h = mmToPx(detection.bbox.height, this.dpi, zoom);

      const color = this.getDetectionColor(detection.type);
      const rect = new Konva.Rect({
        x,
        y,
        width: w,
        height: h,
        stroke: color,
        strokeWidth: 1,
        dash: [4, 4],
        listening: false,
      });
      this.detectionLayer.add(rect);
    }
    this.detectionLayer.draw();
  }

  private getDetectionColor(type?: string): string {
    switch (type) {
      case 'date':
        return '#4caf50';
      case 'currency':
        return '#ff9800';
      case 'number':
        return '#2196f3';
      case 'checkbox':
        return '#9c27b0';
      case 'signature':
        return '#f44336';
      default:
        return '#607d8b';
    }
  }

  zoomIn(): void {
    this.setZoom(this._zoom.value + 0.1);
  }

  zoomOut(): void {
    this.setZoom(this._zoom.value - 0.1);
  }

  toggleSnap(): void {
    this.snapEnabled = !this.snapEnabled;
  }

  undo(): void {
    const entry = this.undoStack.pop();
    if (!entry) return;
    this.applyState(entry.elementId, entry.before);
    this.redoStack.push(entry);
    this._dirty.next(true);
  }

  redo(): void {
    const entry = this.redoStack.pop();
    if (!entry) return;
    this.applyState(entry.elementId, entry.after);
    this.undoStack.push(entry);
    this._dirty.next(true);
  }

  getElementsData(): Record<string, unknown>[] {
    return Array.from(this.elements.values()).map((el) => ({ ...el.data }));
  }

  markClean(): void {
    this._dirty.next(false);
  }

  destroy(): void {
    this.stage?.destroy();
    this.stage = null;
    this.layer = null;
    this.elements.clear();
    this.undoStack = [];
    this.redoStack = [];
  }

  ngOnDestroy(): void {
    this.destroyed$.next();
    this.destroyed$.complete();
    this.destroy();
  }

  private drawGrid(): void {
    if (!this.layer || !this.pageRect) return;
    const gridPx = mmToPx(this.gridSizeMm, this.dpi);
    const w = this.pageRect.width();
    const h = this.pageRect.height();
    const ox = this.pageRect.x();
    const oy = this.pageRect.y();

    for (let x = 0; x <= w; x += gridPx) {
      this.layer.add(
        new Konva.Line({
          points: [ox + x, oy, ox + x, oy + h],
          stroke: '#eee',
          strokeWidth: 0.5,
          listening: false,
        })
      );
    }
    for (let y = 0; y <= h; y += gridPx) {
      this.layer.add(
        new Konva.Line({
          points: [ox, oy + y, ox + w, oy + y],
          stroke: '#eee',
          strokeWidth: 0.5,
          listening: false,
        })
      );
    }
  }

  private pushUndo(entry: UndoEntry): void {
    this.undoStack.push(entry);
    this.redoStack = [];
    if (this.undoStack.length > 50) {
      this.undoStack.shift();
    }
  }

  private applyState(elementId: string, state: Record<string, unknown>): void {
    const el = this.elements.get(elementId);
    if (!el) return;

    if ('x_mm' in state || 'y_mm' in state) {
      const zoom = this._zoom.value;
      if ('x_mm' in state) {
        el.konvaNode.x(mmToPx(state['x_mm'] as number, this.dpi, zoom) + 20);
        el.data['x_mm'] = state['x_mm'];
      }
      if ('y_mm' in state) {
        el.konvaNode.y(mmToPx(state['y_mm'] as number, this.dpi, zoom) + 20);
        el.data['y_mm'] = state['y_mm'];
      }
    }

    Object.assign(el.data, state);
    this.layer?.draw();
  }
}
