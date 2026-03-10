import { Directive, ElementRef, OnInit } from '@angular/core';

@Directive({ selector: 'input[fcAutoDir], textarea[fcAutoDir]', standalone: false })
export class AutoDirDirective implements OnInit {
  constructor(private el: ElementRef<HTMLInputElement | HTMLTextAreaElement>) {}

  ngOnInit(): void {
    this.el.nativeElement.setAttribute('dir', 'auto');
  }
}
