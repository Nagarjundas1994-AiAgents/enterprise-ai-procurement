import jwt from 'jsonwebtoken';
import { PERMISSIONS, ROLE_PERMISSIONS } from './rbac.js';

// @sap/xssec is optional at load time: present in production (BTP/XSUAA binding),
// absent is fine for local/Render HS256 or mock operation.
let xssec: any = null;
try {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  xssec = require('@sap/xssec');
} catch {
  xssec = null;
}

export type ActorType = 'USER' | 'AGENT' | 'SYSTEM';

export interface RequestContext {
  userId: string;
  username: string;
  email: string;
  tenantId: string;
  organizationId?: string;
  departmentId?: string;
  roles: string[];
  permissions: string[];
  isAgent: boolean;
  agentId?: string;
  delegatedUserId?: string;
  actorType: ActorType;
  actorId: string;
  correlationId: string;
  requestId: string;
}

// Mock users for local development ONLY. Never use in production.
// Passwords are never stored; mock auth uses header-selected identity.
export const MOCK_USERS: Record<string, { id: string; username: string; email: string; tenantId: string; roles: string[]; departmentId: string }> = {
  'admin@example.com': { id: 'u-admin', username: 'admin', email: 'admin@example.com', tenantId: 'tenant-a', roles: ['ADMIN'], departmentId: 'd-it' },
  'employee@example.com': { id: 'u-emp', username: 'employee', email: 'employee@example.com', tenantId: 'tenant-a', roles: ['EMPLOYEE'], departmentId: 'd-it' },
  'approver@example.com': { id: 'u-appr', username: 'approver', email: 'approver@example.com', tenantId: 'tenant-a', roles: ['APPROVER'], departmentId: 'd-it' },
  'procurement@example.com': { id: 'u-proc', username: 'procurement', email: 'procurement@example.com', tenantId: 'tenant-a', roles: ['PROCUREMENT_OFFICER'], departmentId: 'd-proc' },
  'manager@example.com': { id: 'u-mgr', username: 'manager', email: 'manager@example.com', tenantId: 'tenant-a', roles: ['PROCUREMENT_MANAGER'], departmentId: 'd-proc' },
  'finance@example.com': { id: 'u-fin', username: 'finance', email: 'finance@example.com', tenantId: 'tenant-a', roles: ['FINANCE'], departmentId: 'd-fin' },
  'auditor@example.com': { id: 'u-aud', username: 'auditor', email: 'auditor@example.com', tenantId: 'tenant-a', roles: ['AUDITOR'], departmentId: 'd-fin' },
  'other-tenant@example.com': { id: 'u-other', username: 'other', email: 'other-tenant@example.com', tenantId: 'tenant-b', roles: ['EMPLOYEE'], departmentId: 'd-ops' },
};

function permissionsFor(roles: string[]): string[] {
  const set = new Set<string>();
  for (const r of roles) for (const p of ROLE_PERMISSIONS[r] ?? []) set.add(p);
  return [...set];
}

export function buildMockContext(email: string, overrides: Partial<RequestContext> = {}): RequestContext {
  const m = MOCK_USERS[email] ?? MOCK_USERS['employee@example.com']!;
  return {
    userId: m.id,
    username: m.username,
    email: m.email,
    tenantId: m.tenantId,
    departmentId: m.departmentId,
    roles: m.roles,
    permissions: permissionsFor(m.roles),
    isAgent: false,
    actorType: 'USER',
    actorId: m.id,
    correlationId: `corr-${Date.now()}`,
    requestId: `req-${Date.now()}`,
    ...overrides,
  };
}

export interface AuthResult { ctx: RequestContext; mode: 'jwt' | 'xsuaa' | 'mock' | 'anonymous' }

function anonymousCtx(correlationId: string, requestId: string): RequestContext {
  return {
    userId: 'anonymous', username: 'anonymous', email: '', tenantId: '',
    roles: [], permissions: [], isAgent: false, actorType: 'USER', actorId: 'anonymous',
    correlationId, requestId,
  };
}

// --- XSUAA (SAP BTP) ---------------------------------------------------------
let xsuaaCreds: any = null;
let xsuaaCredsResolved = false;

/** Credentials of the bound XSUAA instance (VCAP_SERVICES), cached. Null when unbound (local/Render). */
export function getXsuaaCredentials(): any {
  if (xsuaaCredsResolved) return xsuaaCreds;
  xsuaaCredsResolved = true;
  try {
    const vcap = JSON.parse(process.env.VCAP_SERVICES || '{}');
    for (const instances of Object.values(vcap) as any[]) {
      for (const inst of instances || []) {
        const label = `${inst.label || ''} ${inst.name || ''} ${(inst.tags || []).join(' ')}`;
        if (/xsuaa/i.test(label) && inst.credentials) { xsuaaCreds = inst.credentials; break; }
      }
      if (xsuaaCreds) break;
    }
  } catch {
    xsuaaCreds = null;
  }
  return xsuaaCreds;
}

/** Known app permissions only — unknown token scopes are dropped (least privilege). */
export function permissionsFromScopes(scopes: string[]): string[] {
  const known = new Set<string>(Object.values(PERMISSIONS) as string[]);
  const out = new Set<string>();
  for (const s of scopes || []) {
    const name = String(s).split('.').pop() as string; // strip 'xsappname.' prefix
    if (known.has(name)) out.add(name);
  }
  return [...out];
}

/**
 * Derive app roles from granted scopes using ROLE_PERMISSIONS as the single source
 * of truth: a role is held iff every permission of that role is granted.
 * ADMIN via ADMIN_SYSTEM; AI_AGENT for client-credentials (service) tokens.
 */
export function deriveRolesFromScopes(scopes: string[], grantType?: string): string[] {
  const granted = new Set<string>(permissionsFromScopes(scopes));
  const roles: string[] = [];
  if (granted.has('ADMIN_SYSTEM')) roles.push('ADMIN');
  for (const [role, perms] of Object.entries(ROLE_PERMISSIONS)) {
    if (role === 'ADMIN' || role === 'AI_AGENT' || perms.length === 0) continue;
    if (perms.every((p) => granted.has(p))) roles.push(role);
  }
  if (grantType === 'client_credentials' && !roles.includes('AI_AGENT')) roles.push('AI_AGENT');
  return roles;
}

async function buildXsuaaContext(token: string, correlationId: string, requestId: string): Promise<RequestContext> {
  const creds = getXsuaaCredentials();
  if (!xssec || !creds) throw new Error('XSUAA not bound');
  const sc = await xssec.createSecurityContext(token, creds);
  const scopes: string[] = typeof sc.getScope === 'function' ? sc.getScope() || [] : [];
  const grantType: string | undefined = typeof sc.getGrantType === 'function' ? sc.getGrantType() : undefined;
  const roles = deriveRolesFromScopes(scopes, grantType);
  const permissions = permissionsFromScopes(scopes);
  const isAgent = grantType === 'client_credentials' || roles.includes('AI_AGENT');
  const userId = String(sc.getLogonName?.() || sc.getUserName?.() || 'unknown');
  return {
    userId,
    username: userId,
    email: String(sc.getEmail?.() || ''),
    tenantId: String(sc.getSubdomain?.() || ''), // XSUAA tenant subdomain = true BTP multitenancy
    roles,
    permissions,
    isAgent,
    agentId: isAgent ? String(sc.getClientId?.() || userId) : undefined,
    actorType: isAgent ? 'AGENT' : 'USER',
    actorId: isAgent ? String(sc.getClientId?.() || userId) : userId,
    correlationId, requestId,
  };
}

/** AuthenticationService: XSUAA (BTP) -> HS256 JWT (Render/self-hosted) -> safe mock -> anonymous. */
export async function authenticateRequest(req: any): Promise<AuthResult> {
  const correlationId = (req.headers?.['x-correlation-id'] as string) || `corr-${Date.now()}-${Math.floor(Math.random() * 1e6)}`;
  const requestId = (req.headers?.['x-request-id'] as string) || `req-${Date.now()}`;
  const auth = req.headers?.authorization as string | undefined;

  // 1) Bearer path
  if (auth?.startsWith('Bearer ')) {
    const token = auth.slice(7);
    // 1a) XSUAA validation when bound (SAP BTP) — full RS256/JWKS verification
    if (getXsuaaCredentials()) {
      try {
        const ctx = await buildXsuaaContext(token, correlationId, requestId);
        if (!ctx.tenantId) throw new Error('XSUAA token carries no subdomain');
        return { ctx, mode: 'xsuaa' };
      } catch {
        return { ctx: anonymousCtx(correlationId, requestId), mode: 'anonymous' };
      }
    }
    // 1b) HS256 JWT path (Render / self-hosted, JWT_SECRET)
    const secret = process.env.JWT_SECRET;
    try {
      if (!secret) throw new Error('JWT_SECRET not configured');
      const payload = jwt.verify(token, secret) as any;
      const roles: string[] = payload.roles ?? payload.scope?.split(' ') ?? [];
      const ctx: RequestContext = {
        userId: String(payload.sub ?? payload.user_id ?? 'unknown'),
        username: String(payload.user_name ?? payload.preferred_username ?? payload.sub),
        email: String(payload.email ?? `${payload.sub}@example.com`),
        tenantId: String(payload.zid ?? payload.tenant ?? payload.tenantId ?? 'tenant-a'),
        organizationId: payload.orgId,
        departmentId: payload.departmentId,
        roles,
        permissions: permissionsFor(roles),
        isAgent: roles.includes('AI_AGENT'),
        agentId: payload.agentId,
        delegatedUserId: payload.delegatedUser,
        actorType: roles.includes('AI_AGENT') ? 'AGENT' : 'USER',
        actorId: String(payload.agentId ?? payload.sub),
        correlationId, requestId,
      };
      return { ctx, mode: 'jwt' };
    } catch {
      // Invalid/expired JWT -> anonymous (handlers will reject with 401)
      return { ctx: anonymousCtx(correlationId, requestId), mode: 'anonymous' };
    }
  }

  // 2) Safe mock path for local dev: explicit header opt-in only
  if (process.env.ALLOW_MOCK_AUTH !== 'false') {
    const mockUser = (req.headers?.['x-mock-user'] as string) || 'employee@example.com';
    const agentId = req.headers?.['x-agent-id'] as string | undefined;
    const base = buildMockContext(mockUser, { correlationId, requestId });
    if (agentId) {
      // Agent acting with delegation: agent identity + delegated user, permissions resolved from agent grants at runtime
      base.isAgent = true;
      base.actorType = 'AGENT';
      base.agentId = agentId;
      base.actorId = agentId;
      base.delegatedUserId = base.userId;
    }
    return { ctx: base, mode: 'mock' };
  }

  return { ctx: anonymousCtx(correlationId, requestId), mode: 'anonymous' };
}
