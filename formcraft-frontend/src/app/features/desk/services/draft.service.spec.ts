import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

import { environment } from '../../../../environments/environment';
import { DraftResponse, DraftService } from './draft.service';

describe('DraftService', () => {
  let service: DraftService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [DraftService],
    });
    service = TestBed.inject(DraftService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('listDrafts should GET apiUrl without query params and return DraftResponse[]', () => {
    const mockResponse: DraftResponse[] = [
      {
        id: 'draft-1',
        template_id: 'tpl-1',
        template_version: 1,
        operator_id: 'op-1',
        org_id: 'org-1',
        field_values: { a: 'b' },
        completion_percent: 25,
        name: 'Draft 1',
        expires_at: '2026-06-01T00:00:00Z',
        created_at: '2026-06-01T00:00:00Z',
        updated_at: '2026-06-01T00:00:00Z',
      },
    ];

    let actual: DraftResponse[] | undefined;
    service.listDrafts().subscribe((res) => {
      actual = res;
    });

    const req = httpMock.expectOne(`${environment.apiBaseUrl}/desk/drafts`);
    expect(req.request.method).toBe('GET');
    expect(req.request.params.keys().length).toBe(0);
    req.flush(mockResponse);

    expect(actual).toEqual(mockResponse);
  });
});
