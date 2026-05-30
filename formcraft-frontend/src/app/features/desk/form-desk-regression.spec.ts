import { of } from 'rxjs';
import { DashboardComponent } from './dashboard/dashboard.component';
import { HistoryComponent } from './history/history.component';
import { TemplateCard } from './services/desk.service';
import { SubmissionListItem } from './services/history.service';

describe('Classic Form Desk regression behavior', () => {
  const template: TemplateCard = {
    id: 'tpl-001',
    name: 'Account Opening',
    description: 'Daily account form',
    category: 'Accounts',
    status: 'published',
    version: 2,
    language: 'ar',
    country: 'EG',
    updated_at: '2026-05-31T00:00:00Z',
    is_pinned: false,
  };

  it('opens published dashboard template cards in the form filler', () => {
    const router = jasmine.createSpyObj('Router', ['navigate']);
    const component = new DashboardComponent(
      jasmine.createSpyObj('DeskService', ['getDashboard', 'pinTemplate', 'unpinTemplate', 'dismissNotification']),
      jasmine.createSpyObj('MatSnackBar', ['open']),
      jasmine.createSpyObj('TranslateService', ['instant']),
      router,
    );

    component.onCardClick(template);

    expect(router.navigate).toHaveBeenCalledWith(['/desk/fill', 'tpl-001']);
  });

  it('clones a history row into the form filler with source submission context', () => {
    const router = jasmine.createSpyObj('Router', ['navigate']);
    const component = new HistoryComponent(
      jasmine.createSpyObj('HistoryService', ['getSubmissions', 'requestReprint']),
      jasmine.createSpyObj('TranslateService', ['instant']),
      router,
    );
    const row = submissionRow();

    component.onCloneAsNew(row);

    expect(router.navigate).toHaveBeenCalledWith(['/desk/fill', 'tpl-001'], {
      queryParams: { clone: 'sub-001' },
    });
  });

  it('requests a reprint PDF for a history row', () => {
    const historyService = jasmine.createSpyObj('HistoryService', ['getSubmissions', 'requestReprint']);
    historyService.requestReprint.and.returnValue(of(new Blob(['pdf'], { type: 'application/pdf' })));
    spyOn(window.URL, 'createObjectURL').and.returnValue('blob:reprint');
    spyOn(window, 'open').and.returnValue({ print: jasmine.createSpy('print') } as unknown as Window);
    const component = new HistoryComponent(
      historyService,
      jasmine.createSpyObj('TranslateService', ['instant']),
      jasmine.createSpyObj('Router', ['navigate']),
    );
    const row = submissionRow();

    component.onReprint(row);

    expect(historyService.requestReprint).toHaveBeenCalledWith('sub-001');
    expect(window.open).toHaveBeenCalledWith('blob:reprint', '_blank');
  });

  function submissionRow(): SubmissionListItem {
    return {
      id: 'sub-001',
      reference_number: 'FC-2026-05-0042',
      template_id: 'tpl-001',
      template_name: 'Account Opening',
      template_version: 2,
      status: 'printed',
      created_at: '2026-05-31T00:00:00Z',
      key_summary: ['Customer: Test User'],
    };
  }
});
