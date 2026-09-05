import { describe, it, expect } from 'vitest';
import { checkRateLimit } from '../lib/security/rate-limit.js';
import { toHttpError, reqError } from '../lib/security/errors.js';

describe('rate limiting', () => {
  it('allows within limit then rejects', () => {
    const key = `test-${Date.now()}`;
    for (let i = 0; i < 5; i++) checkRateLimit(key, 5);
    expect(() => checkRateLimit(key, 5)).toThrow();
  });
});

describe('error handling', () => {
  it('maps AppError to clean HTTP error', () => {
    const e = reqError('BUDGET_EXCEEDED', 'over budget');
    const h = toHttpError(e);
    expect(h.code).toBe('BUDGET_EXCEEDED');
    expect(h.status).toBe(422);
  });
  it('never leaks DB internals', () => {
    const h = toHttpError(new Error('postgres password=secret connect failed'));
    expect(h.code).toBe('INTERNAL_ERROR');
    expect(JSON.stringify(h)).not.toMatch(/password/i);
  });
});
