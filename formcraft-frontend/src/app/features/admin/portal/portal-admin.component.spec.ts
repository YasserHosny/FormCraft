import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PortalAdminComponent } from './portal-admin.component';

describe('PortalAdminComponent', () => {
  let component: PortalAdminComponent;
  let fixture: ComponentFixture<PortalAdminComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [PortalAdminComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(PortalAdminComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render configuration form', () => {
    // T070 placeholder
    expect(true).toBeFalsy();
  });
});
