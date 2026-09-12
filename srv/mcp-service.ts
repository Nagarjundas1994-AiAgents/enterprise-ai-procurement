import { randomUUID } from 'node:crypto';
import cds from '@sap/cds';
import { authenticateRequest } from '../lib/auth/authentication.js';
import { AuthorizationService } from '../lib/authorization/authorization.js';
import { MCP_TOOL_PERMISSIONS, PERMISSIONS } from '../lib/auth/rbac.js';
import { authorizeAgentTool } from '../lib/agents/agent-auth.js';
import { sendA2AMessage } from '../lib/agents/a2a-client.js';
import { sanitizeForLLM } from '../lib/validation/validation.js';
import { writeAudit } from '../lib/audit/audit.js';
import { checkRateLimit, rateKey } from '../lib/security/rate-limit.js';
import { toHttpError } from '../lib/security/errors.js';

async function ctxOf(req: any) {
  const { ctx } = await authenticateRequest(req.http?.req ?? req);
  AuthorizationService.requireAuth(ctx);
  return ctx;
}

async function guardTool(req: any, toolName: string) {
  const ctx = await ctxOf(req);
  const required = MCP_TOOL_PERMISSIONS[toolName];
  AuthorizationService.requirePermission(ctx, 'EXECUTE_MCP_TOOL');
  AuthorizationService.requirePermission(ctx, required);
  checkRateLimit(rateKey(toolName, ctx.actorId), 60);
  if (ctx.isAgent && ctx.agentId) {
    await authorizeAgentTool(cds.tx(req) as any, ctx, ctx.agentId, toolName);
  }
  return ctx;
}

async function recordMcp(tx: any, ctx: any, toolName: string, input: unknown, output: unknown, status: string, ms: number, error?: string) {
  try {
    const tool: any = await tx.run(SELECT.one.from('procurement.db.MCPTools').where({ name: toolName }));
    await tx.run(INSERT.into('procurement.db.MCPToolExecutions').entries({
            ID: randomUUID(),
tool_ID: tool?.ID ?? null, tenantId: ctx.tenantId, actorType: ctx.actorType,
      actorId: ctx.actorId, agentId: ctx.agentId, input: JSON.stringify(input ?? {}).slice(0, 8000),
      output: JSON.stringify(output ?? {}).slice(0, 8000), status, error, correlationId: ctx.correlationId, durationMs: ms,
    }));
  } catch { /* observability must not break business flow */ }
  await writeAudit(tx, ctx, { action: 'MCP_TOOL_EXECUTED', entity: 'MCPTool', entityId: toolName, newValue: { status }, result: status === 'SUCCESS' ? 'SUCCESS' : 'FAILED' });
}

export default class MCPService extends (cds.ApplicationService as any) {
  async init() {
    // Tenant isolation + RBAC on generic (adapter-driven) reads.
    // The MCP adapter's query tool reads these projections directly, so they
    // need the same guards as the domain services — never rely on the client.
    const readGuard: Record<string, string> = {
      PurchaseRequisitions: PERMISSIONS.READ_PR,
      PurchaseOrders: PERMISSIONS.READ_PR,
      Suppliers: PERMISSIONS.READ_SUPPLIER,
      Invoices: PERMISSIONS.READ_INVOICE,
      Approvals: PERMISSIONS.READ_PR,
      RiskAssessments: PERMISSIONS.READ_PR,
    };
    for (const [entity, permission] of Object.entries(readGuard)) {
      this.before('READ', (this.entities as any)[entity], async (req: any) => {
        const ctx = await ctxOf(req);
        AuthorizationService.requirePermission(ctx, permission);
        req.query.where({ tenantId: ctx.tenantId });
      });
    }
    const wrap = (toolName: string, fn: (req: any, ctx: any, tx: any) => Promise<any>) =>
      this.on(toolName, async (req: any) => {
        const t0 = Date.now();
        let ctx: any;
        try {
          ctx = await guardTool(req, toolName);
          const tx = cds.tx(req);
          const out = await fn(req, ctx, tx);
          await recordMcp(tx, ctx, toolName, req.data, { ok: true }, 'SUCCESS', Date.now() - t0);
          return out;
        } catch (e) {
          const http = toHttpError(e);
          try { if (ctx) await recordMcp(cds.tx(req), ctx, toolName, req.data, http, 'DENIED', Date.now() - t0, http.message); } catch { /* noop */ }
          req.reject(http);
        }
      });

    wrap('searchPurchaseRequisitions', async (req, ctx, tx) => {
      let q = SELECT.from('procurement.db.PurchaseRequisitions').where({ tenantId: ctx.tenantId });
      if (req.data.status) q = SELECT.from('procurement.db.PurchaseRequisitions').where({ tenantId: ctx.tenantId, status: req.data.status });
      const rows: any[] = await tx.run(q.limit(req.data.top ?? 20));
      const s = (req.data.search ?? '').toLowerCase();
      return s ? rows.filter((r) => JSON.stringify(r).toLowerCase().includes(s)).slice(0, req.data.top ?? 20) : rows;
    });

    wrap('getPurchaseRequisition', async (req, ctx, tx) => {
      const row: any = await tx.run(SELECT.one.from('procurement.db.PurchaseRequisitions').where({ ID: req.data.ID, tenantId: ctx.tenantId }));
      if (!row) throw Object.assign(new Error('Not found'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
      return row;
    });

    wrap('createPurchaseRequisition', async (req, ctx, tx) => {
      AuthorizationService.requirePermission(ctx, PERMISSIONS.CREATE_PR);
      const d = req.data;
      if (!d.title) throw Object.assign(new Error('Title required'), { code: 'VALIDATION_ERROR', status: 400 });
      if (Number(d.totalAmount ?? 0) <= 0) throw Object.assign(new Error('Amount must be > 0'), { code: 'VALIDATION_ERROR', status: 400 });
      const prId = randomUUID();
      await tx.run(INSERT.into('procurement.db.PurchaseRequisitions').entries({
        ID: prId,
        requisitionNo: `PR-${Date.now().toString().slice(-6)}`,
        title: d.title, description: d.description, department_ID: d.departmentID,
        tenantId: ctx.tenantId, status: 'DRAFT', totalAmount: d.totalAmount ?? 0,
      }));
      // INSERT returns the row on SQLite but [] on PostgreSQL — re-read by known ID.
      return await tx.run(SELECT.one.from('procurement.db.PurchaseRequisitions').where({ ID: prId }));
    });

    wrap('searchPurchaseOrders', async (req, ctx, tx) => {
      const rows: any[] = await tx.run(SELECT.from('procurement.db.PurchaseOrders').where({ tenantId: ctx.tenantId }).limit(50));
      const s = (req.data.search ?? '').toLowerCase();
      const byStatus = req.data.status ? rows.filter((r) => r.status === req.data.status) : rows;
      return s ? byStatus.filter((r) => JSON.stringify(r).toLowerCase().includes(s)) : byStatus;
    });

    wrap('getPurchaseOrder', async (req, ctx, tx) => {
      const row: any = await tx.run(SELECT.one.from('procurement.db.PurchaseOrders').where({ ID: req.data.ID, tenantId: ctx.tenantId }));
      if (!row) throw Object.assign(new Error('Not found'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
      return row;
    });

    wrap('createPurchaseOrder', async (req, ctx, tx) => {
      // MCP never touches DB directly: delegate to ProcurementService business logic
      const svc = await cds.connect.to('ProcurementService');
      return await (svc as any).tx(req).send('convertToPurchaseOrder', { requisitionID: req.data.requisitionID, supplierID: req.data.supplierID });
    });

    wrap('searchSuppliers', async (req, ctx, tx) => {
      const rows: any[] = await tx.run(SELECT.from('procurement.db.Suppliers').where({ tenantId: ctx.tenantId }).limit(50));
      const s = (req.data.search ?? '').toLowerCase();
      return s ? rows.filter((r) => `${r.name}`.toLowerCase().includes(s)) : rows;
    });

    wrap('getSupplier', async (req, ctx, tx) => {
      const row: any = await tx.run(SELECT.one.from('procurement.db.Suppliers').where({ ID: req.data.ID, tenantId: ctx.tenantId }));
      if (!row) throw Object.assign(new Error('Not found'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
      return row;
    });

    wrap('checkBudget', async (req, ctx, tx) => {
      const b: any = await tx.run(SELECT.one.from('procurement.db.Budgets').where({ department_ID: req.data.departmentID, tenantId: ctx.tenantId }).orderBy({ fiscalYear: 'desc' }));
      if (!b) return false;
      return Number(b.totalAmount) - Number(b.committed) - Number(b.consumed) >= Number(req.data.amount);
    });

    wrap('getInvoiceStatus', async (req, ctx, tx) => {
      const row: any = await tx.run(SELECT.one.from('procurement.db.Invoices').where({ ID: req.data.ID, tenantId: ctx.tenantId }));
      if (!row) throw Object.assign(new Error('Not found'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
      return row;
    });

    wrap('getApprovalStatus', async (req, ctx, tx) => {
      return await tx.read('procurement.db.Approvals').where({ requisition_ID: req.data.requisitionID, tenantId: ctx.tenantId });
    });

    wrap('getProcurementRisk', async (req, ctx, tx) => {
      const pr: any = await tx.run(SELECT.one.from('procurement.db.PurchaseRequisitions').where({ ID: req.data.requisitionID, tenantId: ctx.tenantId }));
      if (!pr) throw Object.assign(new Error('Not found'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
      const amount = Number(pr.totalAmount);
      const riskScore = Math.min(100, Math.round(amount / 20000 + (amount > 500000 ? 30 : 0)));
      const riskLevel = riskScore > 75 ? 'HIGH' : riskScore > 40 ? 'MEDIUM' : 'LOW';
      return { entityType: 'PurchaseRequisitions', entityId: pr.ID, riskScore, riskLevel, reasons: `Amount ${amount}`, recommendation: riskLevel === 'HIGH' ? 'Require human approval' : 'Proceed with checks', tenantId: ctx.tenantId };
    });

    wrap('submitForApproval', async (req, ctx) => {
      const svc = await cds.connect.to('ProcurementService');
      return await (svc as any).tx(req).send('submitRequisition', { ID: req.data.requisitionID });
    });

    // A2A-via-MCP: these tools call the REMOTE agents on :4007 over A2A JSON-RPC
    // and return their (sanitized, advisory-only) JSON as a string. They never
    // bypass authZ/policy: guardTool already enforced EXECUTE_MCP_TOOL + READ_*.
    const remoteBase = () => (process.env.REMOTE_SUPPLIER_AGENT_URL || 'http://localhost:4007').replace(/\/+$/, '');
    wrap('getRemoteSuppliers', async (req) => {
      const reply = await sendA2AMessage(`${remoteBase()}/`, String(req.data.query ?? 'list suppliers'), 15000);
      return sanitizeForLLM(reply.text);
    });

    wrap('getRemoteLogisticsIntel', async (req) => {
      const reply = await sendA2AMessage(`${remoteBase()}/logistics/`, String(req.data.query ?? 'list shipments'), 15000);
      return sanitizeForLLM(reply.text);
    });

    return super.init();
  }
}
