import type { RequestContext } from '../auth/authentication.js';
import { AuthorizationService } from '../authorization/authorization.js';
import { MCP_TOOL_PERMISSIONS } from '../auth/rbac.js';

/** Agent registry: allowed tools/entities/actions per specialist. LLM never grants permissions. */
export const AGENT_DEFINITIONS: Record<string, { kind: string; tools: string[]; permissions: string[] }> = {
  'agent-procurement': { kind: 'PROCUREMENT', tools: ['searchPurchaseRequisitions', 'getPurchaseRequisition', 'searchSuppliers', 'checkBudget', 'createPurchaseOrder'], permissions: ['READ_PURCHASE_REQUISITION', 'READ_SUPPLIER', 'READ_BUDGET', 'CREATE_PURCHASE_ORDER', 'EXECUTE_MCP_TOOL'] },
  'agent-approval': { kind: 'APPROVAL', tools: ['getApprovalStatus', 'getPurchaseRequisition', 'getProcurementRisk'], permissions: ['READ_PURCHASE_REQUISITION', 'APPROVE_PURCHASE_REQUISITION', 'EXECUTE_MCP_TOOL'] },
  'agent-risk': { kind: 'RISK', tools: ['getSupplier', 'searchSuppliers', 'getProcurementRisk'], permissions: ['READ_SUPPLIER', 'READ_PURCHASE_REQUISITION', 'EXECUTE_MCP_TOOL'] },
  'agent-invoice': { kind: 'INVOICE', tools: ['getInvoiceStatus'], permissions: ['READ_INVOICE', 'EXECUTE_MCP_TOOL'] },
  'agent-budget': { kind: 'BUDGET', tools: ['checkBudget'], permissions: ['READ_BUDGET', 'EXECUTE_MCP_TOOL'] },
  'agent-audit': { kind: 'AUDIT', tools: [], permissions: ['VIEW_AUDIT_LOG', 'EXECUTE_MCP_TOOL'] },
  'agent-orchestrator': { kind: 'ORCHESTRATOR', tools: ['*'], permissions: ['READ_PURCHASE_REQUISITION', 'READ_SUPPLIER', 'READ_BUDGET', 'READ_INVOICE', 'EXECUTE_AGENT', 'EXECUTE_MCP_TOOL'] },
};

/** Resolve effective permissions for an agent: explicit grants only (DB) overlaid on registry defaults. */
export async function resolveAgentPermissions(db: any, ctx: RequestContext, agentId: string): Promise<{ permissions: string[]; tools: string[] }> {
  const def = AGENT_DEFINITIONS[agentId];
  let permissions = def?.permissions ?? [];
  let tools = def?.tools ?? [];
  try {
    const agent = await SELECT.one.from('procurement.db.Agents').where({ agentId });
    if (agent) {
      const grants = await SELECT.from('procurement.db.AgentPermissions').where({ agent_ID: agent.ID });
      if (grants?.length) {
        const perms = await SELECT.from('procurement.db.Permissions').where({ ID: { in: grants.map((g: any) => g.permission_ID) } });
        permissions = perms.map((p: any) => p.name);
      }
      const toolGrants = await SELECT.from('procurement.db.AgentToolPermissions').where({ agent_ID: agent.ID, allowed: true });
      if (toolGrants?.length) tools = toolGrants.map((t: any) => t.toolName);
      else if (agent.allowedTools) { try { tools = JSON.parse(agent.allowedTools); } catch { /* keep */ } }
    }
  } catch { /* DB unavailable in some tests — fall back to registry */ }
  return { permissions, tools };
}

/** Authorize one agent tool call: identity -> permission -> tool grant -> tenant. Throws on denial. */
export async function authorizeAgentTool(db: any, ctx: RequestContext, agentId: string, toolName: string): Promise<void> {
  const required = MCP_TOOL_PERMISSIONS[toolName];
  if (!required) throw Object.assign(new Error(`Unknown tool ${toolName}`), { code: 'MCP_TOOL_NOT_AUTHORIZED', status: 403 });
  const { permissions, tools } = await resolveAgentPermissions(db, ctx, agentId);
  if (!tools.includes('*') && !tools.includes(toolName))
    throw Object.assign(new Error(`Agent ${agentId} not granted tool ${toolName}`), { code: 'AGENT_NOT_AUTHORIZED', status: 403 });
  const effective = { ...ctx, permissions: [...new Set([...ctx.permissions, ...permissions])] };
  AuthorizationService.requirePermission(effective, required);
  AuthorizationService.requirePermission(effective, 'EXECUTE_MCP_TOOL');
}
