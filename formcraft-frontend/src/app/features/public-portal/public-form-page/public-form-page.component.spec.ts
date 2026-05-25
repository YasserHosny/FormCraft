import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PublicFormPageComponent } from './public-form-page.component';

describe('PublicFormPageComponent', () => {
  let component: PublicFormPageComponent;
  let fixture: ComponentFixture<PublicFormPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [PublicFormPageComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(PublicFormPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render Flow Layout fields', () => {
    // T035 placeholder
    expect(true).toBeFalsy();
  });
});
