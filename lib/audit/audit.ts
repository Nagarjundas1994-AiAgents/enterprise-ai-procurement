import { randomUUID } from 'node:crypto';
import type { RequestContext } from '../auth/authentication.js';

export interface AuditRecord {
  action: string; entity?: string; entityId?: string;
  oldValue?: unknown; newValue?: unknown; result?: string;
}

function safe(v: unknown): string | undefined {
  if (v === undefined) return undefined;
  try {
    let s = typeof v === 'string' ? v : JSON.stringify(v);
    // mask secrets
    s = s.replace(/(password|secret|api[_-]?key|token|authorization)"?\s*:\s*"[^"]*"/gi, '"$1":"***"');
    return s.slice(0, 8000);
  } catch { return undefined; }
}

export async function writeAudit(db: any, ctx: RequestContext, rec: AuditRecord, req?: any) {
  try {
    await INSERT.into('procurement.db.AuditLogs').entries({
            ID: randomUUID(),
timestamp: new Date().toISOString(),
      tenantId: ctx.tenantId,
      actorType: ctx.actorType,
      actorId: ctx.actorId,
      userId: ctx.userId,
      agentId: ctx.agentId,
      delegatedUserId: ctx.delegatedUserId,
      action: rec.action,
      entity: rec.entity,
      entityId: rec.entityId ? String(rec.entityId) : undefined,
      oldValue: safe(rec.oldValue),
      newValue: safe(rec.newValue),
      result: rec.result ?? 'SUCCESS',
      correlationId: ctx.correlationId,
      requestId: ctx.requestId,
      ipAddress: req?.headers?.['x-forwarded-for'] ?? req?.socket?.remoteAddress ?? undefined,
    });
  } catch (e) {
    console.error('[audit] failed to write audit log', (e as Error).message);
  }
}
