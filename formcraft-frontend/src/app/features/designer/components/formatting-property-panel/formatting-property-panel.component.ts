import { Component, Input } from '@angular/core';
import { CanvasElement, CanvasService } from '../../services/canvas.service';

const BUNDLED_FAMILIES = ['Noto Naskh Arabic', 'Noto Sans'];

@Component({
  selector: 'fc-formatting-property-panel',
  standalone: false,
  templateUrl: './formatting-property-panel.component.html',
  styleUrls: ['./formatting-property-panel.component.scss'],
})
export class FormattingPropertyPanelComponent {
  @Input() element!: CanvasElement;

  overflowOptions = [
    { value: 'clip', labelKey: 'formatting.overflow_clip' },
    { value: 'shrink-to-fit', labelKey: 'formatting.overflow_shrink' },
    { value: 'visible', labelKey: 'formatting.overflow_visible' },
  ];

  constructor(private canvasService: CanvasService) {}

  get fmt(): Record<string, unknown> {
    return (this.element?.data['formatting'] as Record<string, unknown>) || {};
  }

  get font(): Record<string, unknown> {
    return (this.fmt['font'] as Record<string, unknown>) || {};
  }

  get lineLayout(): Record<string, unknown> {
    return (this.fmt['lineLayout'] as Record<string, unknown>) || {};
  }

  get overflow(): string {
    return (this.fmt['overflow'] as string) || '';
  }

  get fontFamily(): string {
    const f = this.font['family'] as string | undefined;
    if (!f) return '';
    return BUNDLED_FAMILIES.includes(f) ? f : 'custom';
  }

  get customFontFamily(): string {
    const f = this.font['family'] as string | undefined;
    if (!f || BUNDLED_FAMILIES.includes(f)) return '';
    return f;
  }

  get fontSize(): number | null {
    const v = this.font['size_pt'];
    return v != null ? Number(v) : null;
  }

  get fontWeight(): 'normal' | 'bold' {
    return (this.font['weight'] as 'normal' | 'bold') || 'normal';
  }

  get fontStyle(): 'normal' | 'italic' {
    return (this.font['style'] as 'normal' | 'italic') || 'normal';
  }

  get fontColor(): string {
    return (this.font['color'] as string) || '';
  }

  get minSizePt(): number | null {
    const v = this.font['min_size_pt'];
    return v != null ? Number(v) : null;
  }

  get maxLines(): number | null {
    const v = this.lineLayout['max_lines'];
    return v != null ? Number(v) : null;
  }

  get firstLineLeftInset(): number | null {
    const v = this.lineLayout['first_line_left_inset_mm'];
    return v != null ? Number(v) : null;
  }

  get lastLineRightInset(): number | null {
    const v = this.lineLayout['last_line_right_inset_mm'];
    return v != null ? Number(v) : null;
  }

  get showBundledWarning(): boolean {
    const f = this.font['family'] as string | undefined;
    return !!f && !BUNDLED_FAMILIES.includes(f);
  }

  get showInsetWarning(): boolean {
    const left = Number(this.firstLineLeftInset || 0);
    const right = Number(this.lastLineRightInset || 0);
    const width = Number(this.element?.data['width_mm'] || 0);
    return width > 0 && left + right >= width;
  }

  onFontFamilyChange(value: string): void {
    if (value === 'custom') {
      this.updateFont({ family: this.customFontFamily || '' });
    } else {
      this.updateFont({ family: value });
    }
  }

  onCustomFontFamilyChange(value: string): void {
    this.updateFont({ family: value });
  }

  onFontSizeChange(value: string): void {
    const num = parseFloat(value);
    this.updateFont({ size_pt: isNaN(num) ? null : num });
  }

  onFontWeightChange(value: 'normal' | 'bold'): void {
    this.updateFont({ weight: value });
  }

  onFontStyleChange(value: 'normal' | 'italic'): void {
    this.updateFont({ style: value });
  }

  onFontColorChange(value: string): void {
    this.updateFont({ color: value || null });
  }

  onMinSizeChange(value: string): void {
    const num = parseFloat(value);
    this.updateFont({ min_size_pt: isNaN(num) ? null : num });
  }

  onMaxLinesChange(value: string): void {
    const num = parseInt(value, 10);
    this.updateLineLayout({ max_lines: isNaN(num) ? null : num });
  }

  onFirstLineLeftInsetChange(value: string): void {
    const num = parseFloat(value);
    this.updateLineLayout({ first_line_left_inset_mm: isNaN(num) ? null : num });
  }

  onLastLineRightInsetChange(value: string): void {
    const num = parseFloat(value);
    this.updateLineLayout({ last_line_right_inset_mm: isNaN(num) ? null : num });
  }

  onOverflowChange(value: string): void {
    this.updateFormatting({ overflow: value || null });
  }

  private updateFont(patch: Record<string, unknown>): void {
    const current = { ...this.font };
    for (const [k, v] of Object.entries(patch)) {
      if (v == null) {
        delete current[k];
      } else {
        current[k] = v;
      }
    }
    this.updateFormatting({ font: Object.keys(current).length ? current : null });
  }

  private updateLineLayout(patch: Record<string, unknown>): void {
    const current = { ...this.lineLayout };
    for (const [k, v] of Object.entries(patch)) {
      if (v == null) {
        delete current[k];
      } else {
        current[k] = v;
      }
    }
    this.updateFormatting({ lineLayout: Object.keys(current).length ? current : null });
  }

  private updateFormatting(patch: Record<string, unknown>): void {
    this.canvasService.updateElementFormatting(this.element.id, patch);
  }
}
