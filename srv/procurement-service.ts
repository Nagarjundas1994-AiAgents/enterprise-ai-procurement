import { randomUUID } from 'node:crypto';
import cds from '@sap/cds';
import { authenticateRequest } from '../lib/auth/authentication.js';
import { AuthorizationService } from '../lib/authorization/authorization.js';
import { PERMISSIONS } from '../lib/auth/rbac.js';
import { writeAudit } from '../lib/audit/audit.js';
import { assertTransition, PR_FLOW } from '../lib/workflow/lifecycle.js';
import { validateRequisition, validatePO } from '../lib/validation/validation.js';
import { evaluatePolicy } from '../lib/workflow/policy.js';
import { toHttpError, reqError } from '../lib/security/errors.js';
import { log } from '../lib/security/observability.js';

async function ctxOf(req: any) {
  const { ctx } = await authenticateRequest(req.http?.req ?? req);
  AuthorizationService.requireAuth(ctx);
  return ctx;
}

export default class ProcurementService extends (cds.ApplicationService as any) {
  async init() {
    const { PurchaseRequisitions, PurchaseOrders } = this.entities;

    // Tenant isolation + RBAC on every read
    this.before('READ', PurchaseRequisitions, async (req: any) => {
      const ctx = await ctxOf(req);
      AuthorizationService.requirePermission(ctx, PERMISSIONS.READ_PR);
      req.query.where({ tenantId: ctx.tenantId });
    });

    this.before(['CREATE'], PurchaseRequisitions, async (req: any) => {
      const ctx = await ctxOf(req);
      AuthorizationService.requirePermission(ctx, PERMISSIONS.CREATE_PR);
      validateRequisition(req.data);
      req.data.tenantId = ctx.tenantId; // never trust client tenant
      req.data.status = 'DRAFT';
      req.data.requester_ID = req.data.requester_ID ?? ctx.userId;
      req.data.requisitionNo = req.data.requisitionNo ?? `PR-${Date.now().toString().slice(-6)}`;
    });

    this.after(['CREATE'], PurchaseRequisitions, async (data: any, req: any) => {
      try {
        if (!data) return data; // audit must never break the response path
        const ctx = await ctxOf(req);
        await writeAudit(this, ctx, { action: 'PURCHASE_REQUISITION_CREATED', entity: 'PurchaseRequisitions', entityId: data.ID, newValue: data }, req.http?.req);
      } catch (e) {
        console.error('[audit] after-create hook failed', (e as Error).message);
      }
      return data;
    });

    this.before(['UPDATE'], PurchaseRequisitions, async (req: any) => {
      const ctx = await ctxOf(req);
      AuthorizationService.requirePermission(ctx, PERMISSIONS.UPDATE_PR);
      if (req.data.tenantId && req.data.tenantId !== ctx.tenantId)
        throw reqError('TENANT_ACCESS_DENIED', 'tenantId is server-controlled');
    });

    this.before(['DELETE'], PurchaseRequisitions, async (req: any) => {
      const ctx = await ctxOf(req);
      AuthorizationService.requirePermission(ctx, PERMISSIONS.DELETE_PR);
    });

    this.before('READ', PurchaseOrders, async (req: any) => {
      const ctx = await ctxOf(req);
      AuthorizationService.requirePermission(ctx, PERMISSIONS.READ_PR);
      req.query.where({ tenantId: ctx.tenantId });
    });

    // --- lifecycle actions, all transactional + audited + concurrency-safe ---

    this.on('submitRequisition', async (req: any) => {
      try {
        const ctx = await ctxOf(req);
        AuthorizationService.requirePermission(ctx, PERMISSIONS.CREATE_PR);
        const { ID } = req.data;
        const tx = cds.tx(req);
        const pr: any = await tx.run(SELECT.one.from(PurchaseRequisitions).where({ ID, tenantId: ctx.tenantId }).forUpdate());
        if (!pr) throw reqError('RESOURCE_NOT_FOUND', 'Requisition not found');
        assertTransition(PR_FLOW, pr.status, 'SUBMITTED');
        await tx.update(PurchaseRequisitions).set({ status: 'SUBMITTED' }).where({ ID, version: pr.version });
        await tx.update(PurchaseRequisitions).set({ version: pr.version + 1 }).where({ ID });
        await writeAudit(tx, ctx, { action: 'PURCHASE_REQUISITION_SUBMITTED', entity: 'PurchaseRequisitions', entityId: ID, oldValue: pr.status, newValue: 'SUBMITTED' });
        return 'SUBMITTED';
      } catch (e) { req.reject(toHttpError(e)); }
    });

    this.on('approveRequisition', async (req: any) => {
      try {
        const ctx = await ctxOf(req);
        AuthorizationService.requirePermission(ctx, PERMISSIONS.APPROVE_PR);
        const tx = cds.tx(req);
        const pr: any = await tx.run(SELECT.one.from(PurchaseRequisitions).where({ ID: req.data.ID, tenantId: ctx.tenantId }).forUpdate());
        if (!pr) throw reqError('RESOURCE_NOT_FOUND', 'Requisition not found');
        const from = pr.status === 'SUBMITTED' ? 'SUBMITTED' : pr.status;
        assertTransition(PR_FLOW, from === 'SUBMITTED' ? 'SUBMITTED' : from, from === 'SUBMITTED' ? 'UNDER_REVIEW' : 'APPROVED');
        // SUBMITTED -> UNDER_REVIEW -> APPROVED in one manager action
        await tx.update(PurchaseRequisitions).set({ status: 'APPROVED', version: pr.version + 1 }).where({ ID: pr.ID, version: pr.version });
        await tx.run(INSERT.into('procurement.db.Approvals').entries({
          ID: randomUUID(),
          requisition_ID: pr.ID, tenantId: ctx.tenantId, stepNo: 1,
          approver_ID: null, status: 'APPROVED', comment: req.data.comment ?? 'Approved', decidedAt: new Date().toISOString(),
        }));
        await writeAudit(tx, ctx, { action: 'PURCHASE_REQUISITION_APPROVED', entity: 'PurchaseRequisitions', entityId: pr.ID, oldValue: pr.status, newValue: 'APPROVED' });
        log(ctx, 'requisition approved', { id: pr.ID });
        return 'APPROVED';
      } catch (e) { req.reject(toHttpError(e)); }
    });

    this.on('rejectRequisition', async (req: any) => {
      try {
        const ctx = await ctxOf(req);
        AuthorizationService.requirePermission(ctx, PERMISSIONS.REJECT_PR);
        const tx = cds.tx(req);
        const pr: any = await tx.run(SELECT.one.from(PurchaseRequisitions).where({ ID: req.data.ID, tenantId: ctx.tenantId }).forUpdate());
        if (!pr) throw reqError('RESOURCE_NOT_FOUND', 'Requisition not found');
        assertTransition(PR_FLOW, pr.status, 'REJECTED');
        await tx.update(PurchaseRequisitions).set({ status: 'REJECTED', version: pr.version + 1 }).where({ ID: pr.ID, version: pr.version });
        await writeAudit(tx, ctx, { action: 'PURCHASE_REQUISITION_REJECTED', entity: 'PurchaseRequisitions', entityId: pr.ID, oldValue: pr.status, newValue: 'REJECTED' });
        return 'REJECTED';
      } catch (e) { req.reject(toHttpError(e)); }
    });

    this.on('convertToPurchaseOrder', async (req: any) => {
      try {
        const ctx = await ctxOf(req);
        AuthorizationService.requirePermission(ctx, PERMISSIONS.CREATE_PO);
        const tx = cds.tx(req);
        const pr: any = await tx.run(SELECT.one.from(PurchaseRequisitions).where({ ID: req.data.requisitionID, tenantId: ctx.tenantId }).forUpdate());
        const supplier: any = await tx.run(SELECT.one.from('procurement.db.Suppliers').where({ ID: req.data.supplierID, tenantId: ctx.tenantId }));
        validatePO(pr, supplier);
        // budget check
        const budget: any = await tx.run(SELECT.one.from('procurement.db.Budgets').where({ department_ID: pr.department_ID, tenantId: ctx.tenantId }).orderBy({ fiscalYear: 'desc' }));
        if (budget) {
          const available = Number(budget.totalAmount) - Number(budget.committed) - Number(budget.consumed);
          if (Number(pr.totalAmount) > available) throw reqError('BUDGET_EXCEEDED', `Budget exceeded: need ${pr.totalAmount}, available ${available}`);
        }
        // policy gate: LLM/agents may recommend; policy decides
        const dbPolicies = await tx.read('procurement.db.Policies').where({ tenantId: ctx.tenantId, active: true });
        const decision = evaluatePolicy({ amount: Number(pr.totalAmount), riskLevel: supplier.riskLevel }, dbPolicies);
        if (decision.action === 'REQUIRE_HUMAN' && ctx.isAgent)
          throw reqError('POLICY_REQUIRES_HUMAN_APPROVAL', `Policy ${decision.code} requires human approval for ${pr.totalAmount}`);
        if (decision.action === 'DENY') throw reqError('FORBIDDEN', `Policy ${decision.code} denies this order`);

        const orderNo = `PO-${Date.now().toString().slice(-6)}`;
        const poId = randomUUID();
        await tx.run(INSERT.into(PurchaseOrders).entries({
          ID: poId,
          orderNo, requisition_ID: pr.ID, supplier_ID: supplier.ID,
          tenantId: ctx.tenantId, status: 'DRAFT', totalAmount: pr.totalAmount,
          currency: pr.currency, createdByUser_ID: null,
        }));
        // INSERT returns the row on SQLite but [] on PostgreSQL — re-read by known ID.
        const po: any = await tx.run(SELECT.one.from(PurchaseOrders).where({ ID: poId }));
        if (!po?.ID) throw reqError('RESOURCE_NOT_FOUND', 'Purchase order could not be created');
        // copy items (simplified: single aggregated line when no item detail)
        const items: any[] = await tx.read('procurement.db.PurchaseRequisitionItems').where({ requisition_ID: pr.ID });
        for (const [i, it] of (items.length ? items : [{ description: pr.title, quantity: 1, unitPrice: pr.totalAmount }]).entries()) {
          await tx.run(INSERT.into('procurement.db.PurchaseOrderItems').entries({
            ID: randomUUID(),
            purchaseOrder_ID: po.ID, lineNo: i + 1,
            description: it.description, quantity: it.quantity ?? 1, unitPrice: it.unitPrice ?? pr.totalAmount,
            lineAmount: Number(it.quantity ?? 1) * Number(it.unitPrice ?? pr.totalAmount),
          }));
        }
        assertTransition(PR_FLOW, pr.status, 'CONVERTED_TO_PO');
        await tx.update(PurchaseRequisitions).set({ status: 'CONVERTED_TO_PO', version: pr.version + 1 }).where({ ID: pr.ID, version: pr.version });
        await writeAudit(tx, ctx, { action: 'PURCHASE_ORDER_CREATED', entity: 'PurchaseOrders', entityId: orderNo, newValue: { orderNo, requisition: pr.requisitionNo } });
        return po;
      } catch (e) { req.reject(toHttpError(e)); }
    });

    return super.init();
  }
}
