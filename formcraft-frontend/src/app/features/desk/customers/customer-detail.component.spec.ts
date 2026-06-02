import { convertToParamMap, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CustomerDetailComponent } from './customer-detail.component';
import { CustomerService } from '../services/customer.service';

describe('CustomerDetailComponent', () => {
  function createComponent(routeSnapshot: any): CustomerDetailComponent {
    const router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    const customerService = jasmine.createSpyObj<CustomerService>('CustomerService', [
      'getById',
      'create',
      'update',
    ]);
    const snackBar = jasmine.createSpyObj<MatSnackBar>('MatSnackBar', ['open']);

    return new CustomerDetailComponent(
      { snapshot: routeSnapshot } as any,
      router,
      customerService,
      snackBar,
    );
  }

  it('enters create mode for the explicit customers/new route without waiting for an id param', () => {
    const component = createComponent({
      data: { mode: 'create' },
      paramMap: convertToParamMap({}),
      routeConfig: { path: 'customers/new' },
    });

    component.ngOnInit();

    expect(component.isNew).toBeTrue();
    expect(component.loading).toBeFalse();
  });
});
