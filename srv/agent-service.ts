import { randomUUID } from 'node:crypto';
import cds from '@sap/cds';
import { authenticateRequest } from '../lib/auth/authentication.js';
import { AuthorizationService } from '../lib/authorization/authorization.js';
import { authorizeAgentTool, AGENT_DEFINITIONS } from '../lib/agents/agent-auth.js';
import { getAIService } from '../lib/agents/ai-service.js';
import { sanitizeForLLM } from '../lib/validation/validation.js';
import { fetchAgentCard, sendA2AMessage } from '../lib/agents/a2a-client.js';
import { evaluatePolicy } from '../lib/workflow/policy.js';
import { writeAudit } from '../lib/audit/audit.js';
import { toHttpError } from '../lib/security/errors.js';

async function ctxOf(req: any) {
  const { ctx } = await authenticateRequest(req.http?.req ?? req);
  AuthorizationService.requireAuth(ctx);
  if (req.http?.req?.headers?.['x-agent-id']) { ctx.isAgent = true; ctx.agentId = req.http.req.headers['x-agent-id'] as string; ctx.actorType = 'AGENT'; ctx.actorId = ctx.agentId; }
  return ctx;
}

// Allowlisted REMOTE A2A agents (other servers). Add more via env, never from client input.
function remoteAgentEndpoint(agentName: string): { base: string; rpc: string } {
  const supplierBase = (process.env.REMOTE_SUPPLIER_AGENT_URL || 'http://localhost:4007').replace(/\/+$/, '');
  const allowlist: Record<string, string> = {
    'remote-supplier-agent': supplierBase,
    'remote-logistics-agent': process.env.REMOTE_LOGISTICS_AGENT_URL || `${supplierBase}/logistics`,
  };
  const base = allowlist[agentName];
  if (!base) throw Object.assign(new Error(`Unknown remote agent ${agentName}`), { code: 'A2A_AGENT_UNKNOWN', status: 404 });
  return { base: base.replace(/\/+$/, ''), rpc: `${base.replace(/\/+$/, '')}/` };
}

// Best-effort remote intel: never throws, never blocks the PO flow on remote failure.
async function fetchRemoteSupplierIntel(query: string): Promise<any> {
  const configured = process.env.REMOTE_SUPPLIER_AGENT_URL;
  if (!configured) return null;
  try {
    const { rpc } = remoteAgentEndpoint('remote-supplier-agent');
    const reply = await sendA2AMessage(rpc, query, 8000);
    const clean = sanitizeForLLM(reply.text);
    try { return JSON.parse(clean); } catch { return { raw: clean.slice(0, 2000) }; }
  } catch (e: any) {
    return { unavailable: true, reason: String(e?.message || e).slice(0, 200) };
  }
}
const specialists: Record<string, (tx: any, ctx: any, payload: any) => Promise<any>> = {
  'agent-procurement': async (tx, ctx, p) => {
    const prs = await tx.run(SELECT.from('procurement.db.PurchaseRequisitions').where({ tenantId: ctx.tenantId }).limit(10));
    return { agent: 'procurement', requisitions: prs.length, recommendation: 'Review pending requisitions, check budget + supplier risk before creating POs.' };
  },
  'agent-budget': async (tx, ctx, p) => {
    const b: any = await tx.run(SELECT.one.from('procurement.db.Budgets').where({ department_ID: p.departmentID, tenantId: ctx.tenantId }).orderBy({ fiscalYear: 'desc' }));
    if (!b) return { budgetAvailable: false, reason: 'No budget found' };
    const available = Number(b.totalAmount) - Number(b.committed) - Number(b.consumed);
    return { budgetAvailable: available >= Number(p.amount ?? 0), remainingBudget: available, budgetConsumed: Number(b.consumed), risk: available < Number(p.amount ?? 0) ? 'OVER' : 'OK' };
  },
  'agent-risk': async (tx, ctx, p) => {
    const s: any = await tx.run(SELECT.one.from('procurement.db.Suppliers').where({ ID: p.supplierID, tenantId: ctx.tenantId }));
    if (!s) return { riskScore: 50, riskLevel: 'MEDIUM', reasons: 'Supplier not found', recommendation: 'Verify supplier' };
    const score = Number(s.riskScore ?? 0) + (Number(s.disputeCount ?? 0) * 10) + ((100 - Number(s.onTimeRate ?? 100)) / 2);
    const clamped = Math.max(0, Math.min(100, Math.round(score)));
    return { riskScore: clamped, riskLevel: clamped > 75 ? 'CRITICAL' : clamped > 50 ? 'HIGH' : clamped > 25 ? 'MEDIUM' : 'LOW', reasons: `onTime ${s.onTimeRate}%, disputes ${s.disputeCount}`, recommendation: clamped > 50 ? 'Require mitigation' : 'Acceptable' };
  },
  'agent-invoice': async (tx, ctx, p) => {
    const { threeWayMatch } = await import('../lib/validation/validation.js');
    const inv: any = await tx.run(SELECT.one.from('procurement.db.Invoices').where({ ID: p.invoiceID, tenantId: ctx.tenantId }));
    if (!inv) return { matched: false, issues: ['Invoice not found'] };
    const poItems: any[] = inv.purchaseOrder_ID ? await tx.read('procurement.db.PurchaseOrderItems').where({ purchaseOrder_ID: inv.purchaseOrder_ID }) : [];
    const receipts: any[] = inv.purchaseOrder_ID ? await tx.read('procurement.db.GoodsReceipts').where({ purchaseOrder_ID: inv.purchaseOrder_ID }) : [];
    let receiptItems: any[] = [];
    for (const r of receipts) receiptItems.push(...(await tx.read('procurement.db.GoodsReceiptItems').where({ receipt_ID: r.ID })));
    const invItems: any[] = await tx.read('procurement.db.InvoiceItems').where({ invoice_ID: inv.ID });
    return threeWayMatch(poItems, receiptItems, invItems);
  },
  'agent-approval': async (tx, ctx, p) => {
    const approvals = await tx.read('procurement.db.Approvals').where({ requisition_ID: p.requisitionID, tenantId: ctx.tenantId });
    return { pending: approvals.filter((a: any) => a.status === 'PENDING').length, approvals: approvals.length, recommendation: 'Escalate high-risk requests; never auto-approve > policy limit.' };
  },
  'agent-audit': async (tx, ctx, p) => {
    AuthorizationService.requirePermission(ctx, 'VIEW_AUDIT_LOG');
    const logs = await tx.run(SELECT.from('procurement.db.AuditLogs').where({ tenantId: ctx.tenantId }).orderBy({ timestamp: 'desc' }).limit(20));
    return { entries: logs.length, sample: logs.slice(0, 5) };
  },
};

export default class AgentService extends (cds.ApplicationService as any) {
  async init() {
    this.on('executeTask', async (req: any) => {
      const t0 = Date.now();
      const ctx = await ctxOf(req);
      const { agentId, intent, payload } = req.data;
      const tx = cds.tx(req);
      try {
        AuthorizationService.requirePermission(ctx, 'EXECUTE_AGENT');
        if (!AGENT_DEFINITIONS[agentId]) throw Object.assign(new Error('Unknown agent'), { code: 'AGENT_NOT_AUTHORIZED', status: 403 });
        // Tool-level authorization: deny here aborts the task (never swallowed).
        const toolForIntent = intent === 'create-po' ? 'createPurchaseOrder' : intent === 'check-budget' ? 'checkBudget' : intent === 'assess-risk' ? 'getProcurementRisk' : 'searchPurchaseRequisitions';
        if (ctx.isAgent || agentId) await authorizeAgentTool(tx as any, { ...ctx, isAgent: true, agentId }, agentId, toolForIntent);
        const clean = sanitizeForLLM(payload ?? intent);
        const ai = getAIService();
        const plan = await ai.generate(`Plan ${intent} for ${clean}`);
        const spec = specialists[agentId];
        if (!spec) throw Object.assign(new Error('Agent not implemented'), { code: 'AGENT_NOT_AUTHORIZED', status: 403 });
        const result = await spec(tx, ctx, typeof payload === 'string' ? JSON.parse(payload || '{}') : (payload ?? {}));
        // Validate AI-influenced output against policy before returning actionable decisions
        if (intent === 'create-po' && result && typeof result === 'object') {
          const dbPolicies = await tx.read('procurement.db.Policies').where({ tenantId: ctx.tenantId, active: true });
          const decision = evaluatePolicy({ amount: Number((payload as any)?.amount ?? 0) }, dbPolicies);
          (result as any).policyDecision = decision.action;
          if (decision.action === 'REQUIRE_HUMAN') (result as any).requiresHumanApproval = true;
        }
        await tx.run(INSERT.into('procurement.db.AgentExecutions').entries({
                    ID: randomUUID(),
agent_ID: null, tenantId: ctx.tenantId, toolName: intent,
          input: JSON.stringify({ intent, payload }).slice(0, 8000),
          output: JSON.stringify({ plan, result }).slice(0, 8000),
          status: 'SUCCESS', startedAt: new Date(t0).toISOString(), completedAt: new Date().toISOString(),
          authorizationDecision: 'ALLOW', correlationId: ctx.correlationId,
        })).catch(() => undefined);
        await writeAudit(tx, ctx, { action: 'AGENT_ACTION_EXECUTED', entity: 'Agent', entityId: agentId, newValue: { intent } });
        return JSON.stringify({ plan, result });
      } catch (e) {
        const http = toHttpError(e);
        req.reject(http);
      }
    });

    this.on('orchestrate', async (req: any) => {
      // Orchestrator: intent -> PR -> authZ -> budget -> supplier -> risk -> policy -> PO? -> audit
      const ctx = await ctxOf(req);
      const tx = cds.tx(req);
      try {
        AuthorizationService.requirePermission(ctx, 'EXECUTE_AGENT');
        const { goal, payload } = req.data;
        const p = typeof payload === 'string' ? JSON.parse(payload || '{}') : (payload ?? {});
        const pr: any = p.requisitionID ? await tx.run(SELECT.one.from('procurement.db.PurchaseRequisitions').where({ ID: p.requisitionID, tenantId: ctx.tenantId })) : null;
        if (!pr) return JSON.stringify({ requiresHumanApproval: false, error: 'Requisition not found' });
        if (pr.status !== 'APPROVED') return JSON.stringify({ requiresHumanApproval: true, reason: `PR status ${pr.status} is not APPROVED`, step: 'check-status' });
        AuthorizationService.requirePermission(ctx, 'CREATE_PURCHASE_ORDER');
        const budget = await specialists['agent-budget'](tx, ctx, { departmentID: pr.department_ID, amount: pr.totalAmount });
        if (!budget.budgetAvailable) return JSON.stringify({ requiresHumanApproval: true, reason: 'Budget insufficient', budget });
        // A2A: ask the REMOTE supplier-network agent for live intel (advisory only).
        let remoteSupplier: any = null;
        if (process.env.REMOTE_SUPPLIER_AGENT_URL) {
          let code: string | undefined;
          if (p.supplierID) {
            const local: any = await tx.run(SELECT.one.from('procurement.db.Suppliers').where({ ID: p.supplierID, tenantId: ctx.tenantId }).columns(['supplierId']));
            code = local?.supplierId || String(p.supplierID);
          }
          remoteSupplier = await fetchRemoteSupplierIntel(code ? `supplier ${code}` : 'list suppliers');
        }
        const dbPolicies = await tx.read('procurement.db.Policies').where({ tenantId: ctx.tenantId, active: true });
        const decision = evaluatePolicy({ amount: Number(pr.totalAmount) }, dbPolicies);
        if (decision.action === 'REQUIRE_HUMAN' || decision.action === 'DENY')
          return JSON.stringify({ requiresHumanApproval: true, policyDecision: decision.action, policy: decision.code, remoteSupplier });
        const svc = await cds.connect.to('ProcurementService');
        const po = await (svc as any).tx(req).send('convertToPurchaseOrder', { requisitionID: pr.ID, supplierID: p.supplierID });
        await writeAudit(tx, ctx, { action: 'AGENT_ACTION_EXECUTED', entity: 'Agent', entityId: 'agent-orchestrator', newValue: { goal } });
        return JSON.stringify({ requiresHumanApproval: false, purchaseOrder: po, budget, policyDecision: decision.action, remoteSupplier });
      } catch (e) {
        const http = toHttpError(e);
        if (http.code === 'POLICY_REQUIRES_HUMAN_APPROVAL') return JSON.stringify({ requiresHumanApproval: true, reason: http.message });
        req.reject(http);
      }
    });

    this.on('callRemoteAgent', async (req: any) => {
      // A2A bridge: main agent -> remote agent on another server -> remote data.
      const ctx = await ctxOf(req);
      try {
        AuthorizationService.requirePermission(ctx, 'EXECUTE_AGENT');
        const { agentName, message } = req.data;
        const { base, rpc } = remoteAgentEndpoint(String(agentName));
        const cleanMsg = sanitizeForLLM(String(message ?? 'list suppliers'));
        const card = await fetchAgentCard(base).catch(() => null);
        const reply = await sendA2AMessage(rpc, cleanMsg, 15000);
        const cleanReply = sanitizeForLLM(reply.text);
        let data: any; try { data = JSON.parse(cleanReply); } catch { data = { raw: cleanReply.slice(0, 4000) }; }
        const tx = cds.tx(req);
        await writeAudit(tx, ctx, { action: 'AGENT_ACTION_EXECUTED', entity: 'Agent', entityId: `remote:${agentName}`, newValue: { message: cleanMsg.slice(0, 300) } }).catch(() => undefined);
        return JSON.stringify({ agent: agentName, card: card ? { name: card.name, version: card.version, skills: (card.skills || []).map((s: any) => s.id || s.name) } : null, data });
      } catch (e) { req.reject(toHttpError(e)); }
    });

    this.on('chat', async (req: any) => {
      const ctx = await ctxOf(req);
      try {
        AuthorizationService.requirePermission(ctx, 'EXECUTE_AGENT');
        const ai = getAIService();
        const reply = await ai.chat([{ role: 'user', content: sanitizeForLLM(req.data.message) }]);
        return reply;
      } catch (e) { req.reject(toHttpError(e)); }
    });

    return super.init();
  }
}
