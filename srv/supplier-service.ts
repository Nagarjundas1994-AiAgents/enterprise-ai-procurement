import cds from '@sap/cds';
import { authenticateRequest } from '../lib/auth/authentication.js';
import { AuthorizationService } from '../lib/authorization/authorization.js';
import { PERMISSIONS } from '../lib/auth/rbac.js';
import { toHttpError } from '../lib/security/errors.js';

async function ctxOf(req: any) {
  const { ctx } = await authenticateRequest(req.http?.req ?? req);
  AuthorizationService.requireAuth(ctx);
  return ctx;
}

export default class SupplierService extends (cds.ApplicationService as any) {
  async init() {
    const { Suppliers } = this.entities;
    this.before('READ', Suppliers, async (req: any) => {
      const ctx = await ctxOf(req);
      AuthorizationService.requirePermission(ctx, PERMISSIONS.READ_SUPPLIER);
      req.query.where({ tenantId: ctx.tenantId });
    });
    this.before(['CREATE', 'UPDATE'], Suppliers, async (req: any) => {
      const ctx = await ctxOf(req);
      AuthorizationService.requirePermission(ctx, req.event === 'CREATE' ? PERMISSIONS.CREATE_SUPPLIER : PERMISSIONS.UPDATE_SUPPLIER);
      if (req.data.tenantId && req.data.tenantId !== ctx.tenantId) throw Object.assign(new Error('tenantId is server-controlled'), { code: 'TENANT_ACCESS_DENIED', status: 403 });
      req.data.tenantId = ctx.tenantId;
    });
    this.on('assessSupplierRisk', async (req: any) => {
      try {
        const ctx = await ctxOf(req);
        AuthorizationService.requirePermission(ctx, PERMISSIONS.READ_SUPPLIER);
        const tx = cds.tx(req);
        const s: any = await tx.run(SELECT.one.from('procurement.db.Suppliers').where({ ID: req.data.supplierID, tenantId: ctx.tenantId }));
        if (!s) throw Object.assign(new Error('Not found'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
        const score = Math.max(0, Math.min(100, Math.round(Number(s.riskScore ?? 0) + Number(s.disputeCount ?? 0) * 10)));
        return { entityType: 'Suppliers', entityId: s.ID, riskScore: score, riskLevel: score > 75 ? 'HIGH' : score > 40 ? 'MEDIUM' : 'LOW', reasons: `disputes=${s.disputeCount} onTime=${s.onTimeRate}`, recommendation: score > 50 ? 'Mitigate' : 'OK', tenantId: ctx.tenantId };
      } catch (e) { req.reject(toHttpError(e)); }
    });
    return super.init();
  }
}
