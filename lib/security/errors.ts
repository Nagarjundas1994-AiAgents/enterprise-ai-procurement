/** AppError with stable machine-readable code. Never leaks internals to clients. */
export class AppError extends Error {
  code: string; status: number;
  constructor(code: string, message: string, status = 400) { super(message); this.code = code; this.status = status; }
}

export const Codes = {
  AUTHENTICATION_REQUIRED: 401, FORBIDDEN: 403, TENANT_ACCESS_DENIED: 403,
  INVALID_STATE_TRANSITION: 409, BUDGET_EXCEEDED: 422, SUPPLIER_INACTIVE: 422,
  MCP_TOOL_NOT_AUTHORIZED: 403, AGENT_NOT_AUTHORIZED: 403,
  POLICY_REQUIRES_HUMAN_APPROVAL: 422, RESOURCE_NOT_FOUND: 404, VALIDATION_ERROR: 400,
  CONFLICT: 409, RATE_LIMITED: 429,
} as const;

export function toHttpError(e: any) {
  if (e?.code && e?.status) return { code: e.code, message: e.message, status: e.status };
  // never leak DB internals
  console.error('[error]', e?.message ?? e);
  return { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred', status: 500 };
}

export function reqError(code: keyof typeof Codes, message: string) {
  return new AppError(code, message, Codes[code]);
}
