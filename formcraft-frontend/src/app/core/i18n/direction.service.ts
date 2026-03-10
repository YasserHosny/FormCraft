import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export type Dir = 'rtl' | 'ltr';

@Injectable({ providedIn: 'root' })
export class DirectionService {
  private dirSubject = new BehaviorSubject<Dir>('rtl');
  dir$: Observable<Dir> = this.dirSubject.asObservable();

  get currentDir(): Dir {
    return this.dirSubject.value;
  }

  setDirection(dir: Dir): void {
    document.documentElement.dir = dir;
    this.dirSubject.next(dir);
  }

  toggleDirection(): void {
    const next = this.currentDir === 'rtl' ? 'ltr' : 'rtl';
    this.setDirection(next);
  }
}
