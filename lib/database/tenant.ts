/** TenantContext: server-side tenant resolution. Tenant comes ONLY from auth context. */
export function resolveTenant(ctx: { tenantId?: string }): string {
  if (!ctx.tenantId) throw Object.assign(new Error('Tenant could not be resolved from auth context'), { code: 'TENANT_ACCESS_DENIED', status: 403 });
  return ctx.tenantId;
}

/** Build a tenant-scoped where clause fragment for manual queries. */
export function tenantFilter(tenantId: string) { return { tenantId }; }
