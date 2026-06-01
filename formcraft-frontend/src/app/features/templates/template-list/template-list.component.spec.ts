import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { TranslateFakeLoader, TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { of } from 'rxjs';

import { TemplateService } from '../../../core/services/template.service';
import { SharedModule } from '../../../shared/shared.module';
import { TemplateListComponent } from './template-list.component';

describe('Classic TemplateListComponent layout', () => {
  let fixture: ComponentFixture<TemplateListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [TemplateListComponent],
      imports: [
        SharedModule,
        NoopAnimationsModule,
        TranslateModule.forRoot({ loader: { provide: TranslateLoader, useClass: TranslateFakeLoader } }),
      ],
      providers: [
        {
          provide: TemplateService,
          useValue: jasmine.createSpyObj<TemplateService>('TemplateService', {
            list: of({ data: [], total: 0, page: 1, limit: 100 }),
          }),
        },
        { provide: Router, useValue: jasmine.createSpyObj<Router>('Router', ['navigate']) },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TemplateListComponent);
    fixture.detectChanges();
  });

  it('keeps the page title and create action out of the global primary toolbar', () => {
    expect(fixture.nativeElement.querySelector('mat-toolbar')).toBeNull();
    expect(fixture.nativeElement.querySelector('.template-page-header')).not.toBeNull();
  });
});
