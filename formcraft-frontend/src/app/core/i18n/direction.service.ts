import { Injectable } from '@angular/core';
import { Directionality } from '@angular/cdk/bidi';
import { BehaviorSubject, Observable } from 'rxjs';

export type Dir = 'rtl' | 'ltr';

@Injectable({ providedIn: 'root' })
export class DirectionService {
  private dirSubject = new BehaviorSubject<Dir>('rtl');
  dir$: Observable<Dir> = this.dirSubject.asObservable();

  constructor(private directionality: Directionality) {}

  get currentDir(): Dir {
    return this.dirSubject.value;
  }

  setDirection(dir: Dir): void {
    document.documentElement.dir = dir;
    document.body.dir = dir;
    (this.directionality as any).value = dir;
    this.directionality.change.emit(dir);
    this.dirSubject.next(dir);
  }

  toggleDirection(): void {
    const next = this.currentDir === 'rtl' ? 'ltr' : 'rtl';
    this.setDirection(next);
  }
}
