import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

import { TemplateService } from '../../../core/services/template.service';
import { TemplateListComponent } from './template-list.component';

describe('Redesign TemplateListComponent', () => {
  let fixture: ComponentFixture<TemplateListComponent>;
  let templateService: jasmine.SpyObj<TemplateService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    templateService = jasmine.createSpyObj<TemplateService>('TemplateService', ['list']);
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    templateService.list.and.returnValue(of({
      data: [
        {
          id: 'tpl-1',
          name: 'نموذج فعلي',
          thumbnail_asset: 'template-thumbnails/tpl-1/cover.webp',
          status: 'submitted_for_review',
          version: 2,
          category: 'accounts',
          updated_at: '2026-05-26T10:00:00Z',
          pages: [{ elements: [{}, {}] }],
        },
      ],
      total: 1,
      page: 1,
      limit: 100,
    }));

    await TestBed.configureTestingModule({
      imports: [TemplateListComponent],
      providers: [
        { provide: TemplateService, useValue: templateService },
        { provide: Router, useValue: router },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TemplateListComponent);
    fixture.detectChanges();
  });

  it('loads templates from the backend service and maps review status for tabs', () => {
    expect(templateService.list).toHaveBeenCalledWith({ limit: 100 });
    expect(fixture.componentInstance.templates[0]).toEqual(jasmine.objectContaining({
      id: 'tpl-1',
      name: 'نموذج فعلي',
      status: 'in-review',
      version: 'v2',
      thumbnailAsset: 'http://localhost:54321/storage/v1/object/public/assets/template-thumbnails/tpl-1/cover.webp',
      pages: 1,
      fields: 2,
    }));
    expect(fixture.componentInstance.statusTabs.find((tab) => tab.key === 'all')?.count).toBe(1);
    expect(fixture.componentInstance.statusTabs.find((tab) => tab.key === 'in-review')?.count).toBe(1);
  });

  it('routes primary actions into the real app surfaces', () => {
    fixture.componentInstance.createTemplate();
    fixture.componentInstance.openTemplate(fixture.componentInstance.templates[0]);

    expect(router.navigate).toHaveBeenCalledWith(['/ui/studio/wizard']);
    expect(router.navigate).toHaveBeenCalledWith(['/ui/studio/designer', 'tpl-1']);
  });

  it('renders the saved template thumbnail image on Spark cards', () => {
    const image = fixture.nativeElement.querySelector('.template-thumbnail') as HTMLImageElement | null;

    expect(image).not.toBeNull();
    expect(image?.getAttribute('src')).toBe(
      'http://localhost:54321/storage/v1/object/public/assets/template-thumbnails/tpl-1/cover.webp',
    );
    expect(image?.getAttribute('alt')).toBe('نموذج فعلي');
    expect(fixture.nativeElement.querySelector('.preview-svg')).toBeNull();
  });
});
