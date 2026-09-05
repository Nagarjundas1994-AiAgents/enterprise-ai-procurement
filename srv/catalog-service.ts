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

export default class CatalogService extends (cds.ApplicationService as any) {
  async init() {
    this.before('READ', '*', async (req: any) => {
      const ctx = await ctxOf(req);
      // tenant-scoped entities get automatic filter
      const tenantEntities = ['Departments', 'Employees', 'Budgets', 'BudgetConsumptions', 'Policies', 'PolicyViolations', 'Notifications'];
      const name = req.target?.name?.split('.').pop();
      if (tenantEntities.includes(name)) req.query.where({ tenantId: ctx.tenantId });
    });
    this.on('checkBudget', async (req: any) => {
      try {
        const ctx = await ctxOf(req);
        AuthorizationService.requirePermission(ctx, PERMISSIONS.READ_BUDGET);
        const tx = cds.tx(req);
        const b: any = await tx.run(SELECT.one.from('procurement.db.Budgets').where({ department_ID: req.data.departmentID, tenantId: ctx.tenantId }).orderBy({ fiscalYear: 'desc' }));
        if (!b) return false;
        return Number(b.totalAmount) - Number(b.committed) - Number(b.consumed) >= Number(req.data.amount);
      } catch (e) { req.reject(toHttpError(e)); }
    });
    return super.init();
  }
}
