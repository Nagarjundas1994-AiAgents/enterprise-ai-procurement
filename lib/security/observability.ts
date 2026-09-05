/** Structured request logging: requestId/correlationId/tenant/actor on every line. */
export function log(ctx: Partial<{ requestId: string; correlationId: string; tenantId: string; actorId: string; actorType: string }>, msg: string, extra?: unknown) {
  const base = {
    ts: new Date().toISOString(),
    requestId: ctx.requestId, correlationId: ctx.correlationId,
    tenantId: ctx.tenantId, actorId: ctx.actorId, actorType: ctx.actorType, msg,
  };
  if (extra !== undefined) console.log(JSON.stringify({ ...base, extra }));
  else console.log(JSON.stringify(base));
}
