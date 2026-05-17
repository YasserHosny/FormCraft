import { Injectable } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { BehaviorSubject, Observable, Subscription } from 'rxjs';
import { debounceTime } from 'rxjs/operators';
import { AuthService } from '../../../core/auth/auth.service';

export interface Condition {
  field: string;
  operator: string;
  value: string | number | boolean | null;
}

export interface ConditionObject {
  conditions: Condition[];
  logic: 'AND';
}

export interface ConditionalElement {
  key: string;
  required?: boolean;
  visible_when?: ConditionObject | null;
  required_when?: ConditionObject | null;
  computed_value?: string | null;
  default_value?: string | null;
  placeholder_text?: { ar: string; en: string } | null;
}

@Injectable({ providedIn: 'root' })
export class ConditionEngineService {
  private dependencyGraph: Map<string, string[]> = new Map();
  private elements: ConditionalElement[] = [];
  private form: FormGroup | null = null;
  private subscription: Subscription | null = null;

  private visibilitySubject = new BehaviorSubject<Set<string>>(new Set());
  private requiredSubject = new BehaviorSubject<Set<string>>(new Set());

  visibilityChanged$: Observable<Set<string>> = this.visibilitySubject.asObservable();
  requiredChanged$: Observable<Set<string>> = this.requiredSubject.asObservable();

  constructor(private authService: AuthService) {}

  initialize(elements: ConditionalElement[], form: FormGroup): void {
    this.destroy();
    this.elements = elements;
    this.form = form;
    this.buildDependencyGraph();
    this.evaluateAll();

    this.subscription = form.valueChanges
      .pipe(debounceTime(50))
      .subscribe((values) => this.onFormChange(values));
  }

  destroy(): void {
    this.subscription?.unsubscribe();
    this.subscription = null;
    this.dependencyGraph.clear();
  }

  resolveDefaults(elements: ConditionalElement[], currentLang: string): Record<string, any> {
    const defaults: Record<string, any> = {};
    const user = this.authService.getCurrentUser();

    for (const elem of elements) {
      if (!elem.default_value) continue;
      defaults[elem.key] = this.resolveToken(elem.default_value, user);
    }
    return defaults;
  }

  getPlaceholder(elem: ConditionalElement, lang: string): string {
    if (!elem.placeholder_text) return '';
    return lang === 'en' ? (elem.placeholder_text.en || '') : (elem.placeholder_text.ar || '');
  }

  evaluateExpression(expr: string, values: Record<string, any>): number {
    const tokens = this.tokenize(expr);
    const result = this.parseAddSub(tokens, values);
    return isNaN(result) ? 0 : result;
  }

  private buildDependencyGraph(): void {
    this.dependencyGraph.clear();
    for (const elem of this.elements) {
      const deps = this.extractDependencies(elem);
      for (const dep of deps) {
        const existing = this.dependencyGraph.get(dep) || [];
        if (!existing.includes(elem.key)) {
          existing.push(elem.key);
        }
        this.dependencyGraph.set(dep, existing);
      }
    }
  }

  private extractDependencies(elem: ConditionalElement): string[] {
    const deps: string[] = [];
    if (elem.visible_when) {
      for (const c of elem.visible_when.conditions) {
        deps.push(c.field);
      }
    }
    if (elem.required_when) {
      for (const c of elem.required_when.conditions) {
        if (!deps.includes(c.field)) deps.push(c.field);
      }
    }
    if (elem.computed_value) {
      const refs = this.getExpressionReferences(elem.computed_value);
      for (const r of refs) {
        if (!deps.includes(r)) deps.push(r);
      }
    }
    return deps;
  }

  private getExpressionReferences(expr: string): string[] {
    const refs: string[] = [];
    const identRegex = /[a-zA-Z_][a-zA-Z0-9_]*/g;
    let match: RegExpExecArray | null;
    while ((match = identRegex.exec(expr)) !== null) {
      if (!refs.includes(match[0])) refs.push(match[0]);
    }
    return refs;
  }

  private onFormChange(values: Record<string, any>): void {
    this.evaluateAll(values);
  }

  private evaluateAll(values?: Record<string, any>): void {
    const formData = values || this.form?.value || {};
    const visibleKeys = this.evaluateVisibility(formData);
    const requiredKeys = this.evaluateRequired(formData, visibleKeys);

    this.visibilitySubject.next(visibleKeys);
    this.requiredSubject.next(requiredKeys);

    this.updateComputedValues(formData);
  }

  private evaluateVisibility(formData: Record<string, any>, depth = 0): Set<string> {
    if (depth > 10) return new Set(this.elements.map((e) => e.key));

    const visible = new Set<string>();
    for (const elem of this.elements) {
      if (this.evaluateCondition(elem.visible_when, formData)) {
        visible.add(elem.key);
      }
    }
    return visible;
  }

  private evaluateRequired(formData: Record<string, any>, visibleKeys: Set<string>): Set<string> {
    const required = new Set<string>();
    for (const elem of this.elements) {
      if (!visibleKeys.has(elem.key)) continue;
      if (elem.required) {
        required.add(elem.key);
      } else if (elem.required_when) {
        if (this.evaluateCondition(elem.required_when, formData)) {
          required.add(elem.key);
        }
      }
    }
    return required;
  }

  private evaluateCondition(condition: ConditionObject | null | undefined, formData: Record<string, any>): boolean {
    if (!condition || !condition.conditions || condition.conditions.length === 0) {
      return true;
    }
    return condition.conditions.every((c) => this.evaluateSingle(c, formData));
  }

  private evaluateSingle(condition: Condition, formData: Record<string, any>): boolean {
    const actual = formData[condition.field];
    const expected = condition.value;

    switch (condition.operator) {
      case 'is_empty':
        return actual === null || actual === undefined || actual === '';
      case 'is_not_empty':
        return actual !== null && actual !== undefined && actual !== '';
      case 'equals':
        return String(actual ?? '') === String(expected ?? '');
      case 'not_equals':
        return String(actual ?? '') !== String(expected ?? '');
      case 'contains':
        return actual ? String(actual).toLowerCase().includes(String(expected ?? '').toLowerCase()) : false;
      case 'greater_than':
        return this.toNumber(actual) > this.toNumber(expected);
      case 'less_than':
        return this.toNumber(actual) < this.toNumber(expected);
      default:
        return false;
    }
  }

  private updateComputedValues(formData: Record<string, any>): void {
    if (!this.form) return;
    for (const elem of this.elements) {
      if (!elem.computed_value) continue;
      const numericValues: Record<string, number> = {};
      const refs = this.getExpressionReferences(elem.computed_value);
      for (const ref of refs) {
        numericValues[ref] = this.toNumber(formData[ref]);
      }
      const result = this.evaluateExpression(elem.computed_value, numericValues);
      const control = this.form.get(elem.key);
      if (control && control.value !== result) {
        control.setValue(result, { emitEvent: false });
      }
    }
  }

  private resolveToken(token: string, user: any): any {
    switch (token) {
      case '{{today}}':
        return new Date().toISOString().split('T')[0];
      case '{{now}}':
        return new Date().toISOString();
      case '{{user_name}}':
        return user?.display_name || '';
      case '{{user_email}}':
        return user?.email || '';
      case '{{org_name}}':
        return user?.org_name || '';
      default:
        return token;
    }
  }

  private toNumber(val: any): number {
    const n = Number(val);
    return isNaN(n) ? 0 : n;
  }

  // --- Expression Parser (recursive descent) ---

  private tokenize(expr: string): string[] {
    const tokens: string[] = [];
    let i = 0;
    while (i < expr.length) {
      if (/\s/.test(expr[i])) { i++; continue; }
      if ('+-*/()'.includes(expr[i])) {
        tokens.push(expr[i]);
        i++;
      } else if (/[0-9.]/.test(expr[i])) {
        let num = '';
        while (i < expr.length && /[0-9.]/.test(expr[i])) { num += expr[i]; i++; }
        tokens.push(num);
      } else if (/[a-zA-Z_]/.test(expr[i])) {
        let id = '';
        while (i < expr.length && /[a-zA-Z0-9_]/.test(expr[i])) { id += expr[i]; i++; }
        tokens.push(id);
      } else {
        i++;
      }
    }
    return tokens;
  }

  private parseAddSub(tokens: string[], values: Record<string, any>): number {
    const ctx = { pos: 0, tokens };
    return this.addSub(ctx, values);
  }

  private addSub(ctx: { pos: number; tokens: string[] }, values: Record<string, any>): number {
    let left = this.mulDiv(ctx, values);
    while (ctx.pos < ctx.tokens.length && (ctx.tokens[ctx.pos] === '+' || ctx.tokens[ctx.pos] === '-')) {
      const op = ctx.tokens[ctx.pos++];
      const right = this.mulDiv(ctx, values);
      left = op === '+' ? left + right : left - right;
    }
    return left;
  }

  private mulDiv(ctx: { pos: number; tokens: string[] }, values: Record<string, any>): number {
    let left = this.unary(ctx, values);
    while (ctx.pos < ctx.tokens.length && (ctx.tokens[ctx.pos] === '*' || ctx.tokens[ctx.pos] === '/')) {
      const op = ctx.tokens[ctx.pos++];
      const right = this.unary(ctx, values);
      if (op === '/') {
        left = right === 0 ? 0 : left / right;
      } else {
        left = left * right;
      }
    }
    return left;
  }

  private unary(ctx: { pos: number; tokens: string[] }, values: Record<string, any>): number {
    if (ctx.tokens[ctx.pos] === '-') {
      ctx.pos++;
      return -this.primary(ctx, values);
    }
    if (ctx.tokens[ctx.pos] === '+') {
      ctx.pos++;
    }
    return this.primary(ctx, values);
  }

  private primary(ctx: { pos: number; tokens: string[] }, values: Record<string, any>): number {
    const token = ctx.tokens[ctx.pos];
    if (token === '(') {
      ctx.pos++;
      const val = this.addSub(ctx, values);
      if (ctx.tokens[ctx.pos] === ')') ctx.pos++;
      return val;
    }
    ctx.pos++;
    if (/^[0-9]/.test(token)) {
      return parseFloat(token) || 0;
    }
    return this.toNumber(values[token]);
  }
}
