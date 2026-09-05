/** Minimal in-memory token bucket per tool+actor. Single-instance safe; use Redis in multi-instance prod. */
const buckets = new Map<string, { count: number; resetAt: number }>();

export function checkRateLimit(key: string, limitPerMin = 60) {
  const now = Date.now();
  const b = buckets.get(key);
  if (!b || now > b.resetAt) {
    buckets.set(key, { count: 1, resetAt: now + 60_000 });
    return;
  }
  b.count += 1;
  if (b.count > limitPerMin) {
    throw Object.assign(new Error('Rate limit exceeded'), { code: 'RATE_LIMITED', status: 429 });
  }
}

export function rateKey(tool: string, actorId: string) { return `${tool}:${actorId}`; }
