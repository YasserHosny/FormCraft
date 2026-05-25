import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { PortalService } from './portal.service';

describe('PortalService', () => {
  let service: PortalService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [PortalService],
    });
    service = TestBed.inject(PortalService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should load public form', () => {
    // T034 placeholder
    expect(true).toBeFalsy();
  });

  it('should submit public form', () => {
    // T034 placeholder
    expect(true).toBeFalsy();
  });

  it('should download PDF', () => {
    // T034 placeholder
    expect(true).toBeFalsy();
  });
});
