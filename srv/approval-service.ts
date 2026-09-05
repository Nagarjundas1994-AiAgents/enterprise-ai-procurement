import cds from '@sap/cds';
import { authenticateRequest } from '../lib/auth/authentication.js';
import { AuthorizationService } from '../lib/authorization/authorization.js';
import { PERMISSIONS } from '../lib/auth/rbac.js';
import { writeAudit } from '../lib/audit/audit.js';
import { toHttpError } from '../lib/security/errors.js';

async function ctxOf(req: any) {
  const { ctx } = await authenticateRequest(req.http?.req ?? req);
  AuthorizationService.requireAuth(ctx);
  return ctx;
}

export default class ApprovalService extends (cds.ApplicationService as any) {
  async init() {
    const { Approvals } = this.entities;
    this.before('READ', Approvals, async (req: any) => {
      const ctx = await ctxOf(req);
      AuthorizationService.requirePermission(ctx, PERMISSIONS.READ_PR);
      req.query.where({ tenantId: ctx.tenantId });
    });
    this.on('decideApproval', async (req: any) => {
      try {
        const ctx = await ctxOf(req);
        AuthorizationService.requirePermission(ctx, PERMISSIONS.APPROVE_PR);
        const tx = cds.tx(req);
        const ap: any = await tx.run(SELECT.one.from('procurement.db.Approvals').where({ ID: req.data.approvalID, tenantId: ctx.tenantId }).forUpdate());
        if (!ap) throw Object.assign(new Error('Approval not found'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
        if (ap.status !== 'PENDING') throw Object.assign(new Error(`Already ${ap.status}`), { code: 'INVALID_STATE_TRANSITION', status: 409 });
        const decision = String(req.data.decision).toUpperCase() === 'APPROVE' ? 'APPROVED' : 'REJECTED';
        await tx.update('procurement.db.Approvals').set({ status: decision, comment: req.data.comment, decidedAt: new Date().toISOString() }).where({ ID: ap.ID });
        await writeAudit(tx, ctx, { action: decision === 'APPROVED' ? 'PURCHASE_REQUISITION_APPROVED' : 'PURCHASE_REQUISITION_REJECTED', entity: 'Approvals', entityId: ap.ID, newValue: decision });
        return decision;
      } catch (e) { req.reject(toHttpError(e)); }
    });
    return super.init();
  }
}
