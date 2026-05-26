import { Component } from '@angular/core';

@Component({
  standalone: false,
  selector: 'app-batch-schedule-admin',
  templateUrl: './batch-schedule-admin.component.html',
  styleUrls: ['./batch-schedule-admin.component.scss'],
})
export class BatchScheduleAdminComponent {
  schedules: any[] = [];
}
