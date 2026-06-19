import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FormattingPropertyPanelComponent } from './formatting-property-panel.component';
import { CanvasElement, CanvasService } from '../../services/canvas.service';

describe('FormattingPropertyPanelComponent', () => {
  let component: FormattingPropertyPanelComponent;
  let fixture: ComponentFixture<FormattingPropertyPanelComponent>;
  let canvas: jasmine.SpyObj<CanvasService>;

  function makeElement(formatting: Record<string, unknown> = {}, widthMm = 90): CanvasElement {
    return {
      id: 'el-1',
      data: { width_mm: widthMm, formatting },
    } as unknown as CanvasElement;
  }

  beforeEach(async () => {
    canvas = jasmine.createSpyObj<CanvasService>('CanvasService', [
      'updateElementFormatting',
    ]);

    await TestBed.configureTestingModule({
      declarations: [FormattingPropertyPanelComponent],
      providers: [{ provide: CanvasService, useValue: canvas }],
    })
      // Skip the Material/translate template — we are testing class logic.
      .overrideComponent(FormattingPropertyPanelComponent, {
        set: { template: '' },
      })
      .compileComponents();

    fixture = TestBed.createComponent(FormattingPropertyPanelComponent);
    component = fixture.componentInstance;
  });

  it('creates', () => {
    component.element = makeElement();
    expect(component).toBeTruthy();
  });

  describe('font getters', () => {
    it('reads font properties from formatting.font', () => {
      component.element = makeElement({
        font: { size_pt: 13, weight: 'bold', style: 'italic', color: '#333' },
      });
      expect(component.fontSize).toBe(13);
      expect(component.fontWeight).toBe('bold');
      expect(component.fontStyle).toBe('italic');
      expect(component.fontColor).toBe('#333');
    });

    it('defaults weight/style to normal when absent', () => {
      component.element = makeElement({ font: {} });
      expect(component.fontWeight).toBe('normal');
      expect(component.fontStyle).toBe('normal');
    });

    it('maps a bundled family to its name', () => {
      component.element = makeElement({ font: { family: 'Noto Sans' } });
      expect(component.fontFamily).toBe('Noto Sans');
      expect(component.customFontFamily).toBe('');
    });

    it('maps a non-bundled family to "custom" and exposes the raw value', () => {
      component.element = makeElement({ font: { family: 'Courier' } });
      expect(component.fontFamily).toBe('custom');
      expect(component.customFontFamily).toBe('Courier');
      expect(component.showBundledWarning).toBeTrue();
    });
  });

  describe('inset warning', () => {
    it('warns when left + right insets meet or exceed the box width', () => {
      component.element = makeElement(
        { lineLayout: { first_line_left_inset_mm: 50, last_line_right_inset_mm: 45 } },
        90,
      );
      expect(component.showInsetWarning).toBeTrue();
    });

    it('does not warn when insets fit', () => {
      component.element = makeElement(
        { lineLayout: { first_line_left_inset_mm: 22, last_line_right_inset_mm: 26 } },
        90,
      );
      expect(component.showInsetWarning).toBeFalse();
    });
  });

  describe('change handlers', () => {
    beforeEach(() => {
      component.element = makeElement();
    });

    it('emits font size patch', () => {
      component.onFontSizeChange('13');
      expect(canvas.updateElementFormatting).toHaveBeenCalledWith('el-1', {
        font: { size_pt: 13 },
      });
    });

    it('treats a non-numeric size as null (clears it)', () => {
      component.element = makeElement({ font: { size_pt: 13 } });
      component.onFontSizeChange('');
      // size_pt removed → font object now empty → font cleared to null
      expect(canvas.updateElementFormatting).toHaveBeenCalledWith('el-1', {
        font: null,
      });
    });

    it('emits overflow policy patch', () => {
      component.onOverflowChange('shrink-to-fit');
      expect(canvas.updateElementFormatting).toHaveBeenCalledWith('el-1', {
        overflow: 'shrink-to-fit',
      });
    });

    it('clears overflow when set to empty', () => {
      component.onOverflowChange('');
      expect(canvas.updateElementFormatting).toHaveBeenCalledWith('el-1', {
        overflow: null,
      });
    });

    it('emits line inset patch', () => {
      component.onFirstLineLeftInsetChange('22');
      expect(canvas.updateElementFormatting).toHaveBeenCalledWith('el-1', {
        lineLayout: { first_line_left_inset_mm: 22 },
      });
    });

    it('passes a custom family through on custom selection', () => {
      component.element = makeElement({ font: { family: 'Courier' } });
      component.onFontFamilyChange('custom');
      expect(canvas.updateElementFormatting).toHaveBeenCalledWith('el-1', {
        font: { family: 'Courier' },
      });
    });
  });
});
