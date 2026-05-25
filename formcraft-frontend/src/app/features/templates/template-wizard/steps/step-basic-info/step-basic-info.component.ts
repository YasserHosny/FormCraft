import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
  selector: 'fc-step-basic-info',
  standalone: false,
  templateUrl: './step-basic-info.component.html',
  styleUrls: ['./step-basic-info.component.scss'],
})
export class StepBasicInfoComponent {
  @Input() form!: FormGroup;
  @Input() categories: { id: string; name: string }[] = [];
  @Output() clearState = new EventEmitter<void>();

  get tagsControl() {
    return this.form.get('tags');
  }

  addTag(event: any): void {
    const value = (event.value || '').trim();
    if (!value) return;
    const tags = this.form.value.tags || [];
    if (tags.length >= 10) return;
    if (value.length > 30) return;
    if (!tags.includes(value)) {
      this.form.patchValue({ tags: [...tags, value] });
    }
    event.chipInput!.clear();
  }

  removeTag(tag: string): void {
    const tags = (this.form.value.tags || []).filter((t: string) => t !== tag);
    this.form.patchValue({ tags });
  }

  onClear(): void {
    this.clearState.emit();
  }
}
