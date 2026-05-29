import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'fc-classic-redirect',
  standalone: true,
  template: '<p style="padding:24px;color:var(--fc-text-3)">جارٍ التحويل...</p>',
})
export class ClassicRedirectComponent implements OnInit {
  constructor(private route: ActivatedRoute, private router: Router) {}

  ngOnInit(): void {
    let classicRoute = this.route.snapshot.data['classicRoute'] as string || '/templates';
    const params = this.route.snapshot.paramMap;
    params.keys.forEach((key) => {
      classicRoute = classicRoute.replace(`:${key}`, params.get(key) || '');
    });
    this.router.navigate([classicRoute], {
      replaceUrl: true,
      queryParams: this.route.snapshot.queryParams,
    });
  }
}
