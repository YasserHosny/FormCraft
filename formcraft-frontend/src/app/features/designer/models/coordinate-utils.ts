const MM_PER_INCH = 25.4;

export function mmToPx(mm: number, dpi: number = 96, zoom: number = 1): number {
  return (mm / MM_PER_INCH) * dpi * zoom;
}

export function pxToMm(px: number, dpi: number = 96, zoom: number = 1): number {
  return (px / dpi / zoom) * MM_PER_INCH;
}

export function snapToGrid(value: number, gridSize: number): number {
  return Math.round(value / gridSize) * gridSize;
}

export function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

export const MIN_ELEMENT_SIZE_MM = 2;
