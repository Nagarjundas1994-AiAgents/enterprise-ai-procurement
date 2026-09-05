import type { RequestContext } from '../auth/authentication.js';

export class AuthError extends Error {
  code: string; status: number;
  constructor(code: string, message: string, status = 403) { super(message); this.code = code; this.status = status; }
}

/** AuthorizationService — business-layer RBAC. Never rely on frontend checks. */
export const AuthorizationService = {
  hasRole(ctx: RequestContext, role: string) { return ctx.roles.includes(role) || ctx.roles.includes('ADMIN'); },
  hasPermission(ctx: RequestContext, permission: string) {
    return ctx.permissions.includes(permission) || ctx.permissions.includes('ADMIN_SYSTEM');
  },
  requireAuth(ctx: RequestContext) {
    if (!ctx.userId || ctx.userId === 'anonymous' || !ctx.tenantId)
      throw new AuthError('AUTHENTICATION_REQUIRED', 'Authentication required', 401);
  },
  requireRole(ctx: RequestContext, role: string) {
    this.requireAuth(ctx);
    if (!this.hasRole(ctx, role)) throw new AuthError('FORBIDDEN', `Role ${role} required`, 403);
  },
  requirePermission(ctx: RequestContext, permission: string) {
    this.requireAuth(ctx);
    if (!this.hasPermission(ctx, permission))
      throw new AuthError('FORBIDDEN', `Permission ${permission} required`, 403);
  },
  canRead: (ctx: RequestContext, p: string) => AuthorizationService.hasPermission(ctx, p),
  canCreate: (ctx: RequestContext, p: string) => AuthorizationService.hasPermission(ctx, p),
  canUpdate: (ctx: RequestContext, p: string) => AuthorizationService.hasPermission(ctx, p),
  canDelete: (ctx: RequestContext, p: string) => AuthorizationService.hasPermission(ctx, p),
  canApprove(ctx: RequestContext) {
    return this.hasPermission(ctx, 'APPROVE_PURCHASE_REQUISITION');
  },
  canExecuteTool(ctx: RequestContext, tool: string, agentGrant?: { allowed: boolean }) {
    this.requirePermission(ctx, 'EXECUTE_MCP_TOOL');
    if (ctx.isAgent && agentGrant && !agentGrant.allowed)
      throw new AuthError('MCP_TOOL_NOT_AUTHORIZED', `Agent not authorized for tool ${tool}`, 403);
  },
  /** Tenant guard: never trust client-supplied tenantId. */
  enforceTenant(ctx: RequestContext, rowTenantId: string) {
    this.requireAuth(ctx);
    if (rowTenantId && rowTenantId !== ctx.tenantId)
      throw new AuthError('TENANT_ACCESS_DENIED', 'Cross-tenant access denied', 403);
  },
};
