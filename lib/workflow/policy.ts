/** Lightweight policy engine. Policies live in DB (Policies entity); thresholds configurable, never hard-coded in prompts. */
export interface PolicyRule {
  code: string; action: 'AUTO_APPROVE' | 'REQUIRE_MANAGER' | 'REQUIRE_FINANCE' | 'REQUIRE_HUMAN' | 'DENY';
  conditions: { maxAmount?: number; minAmount?: number; riskLevels?: string[]; departments?: string[] };
  priority: number; active: boolean;
}

const DEFAULT_POLICIES: PolicyRule[] = [
  { code: 'PO_AUTO', action: 'AUTO_APPROVE', conditions: { maxAmount: 50000 }, priority: 10, active: true },
  { code: 'PO_MANAGER', action: 'REQUIRE_MANAGER', conditions: { minAmount: 50000, maxAmount: 500000 }, priority: 20, active: true },
  { code: 'PO_SENIOR', action: 'REQUIRE_HUMAN', conditions: { minAmount: 500000, maxAmount: 1000000 }, priority: 30, active: true },
  { code: 'PO_EXEC', action: 'REQUIRE_HUMAN', conditions: { minAmount: 1000000 }, priority: 40, active: true },
  { code: 'PO_HIGH_RISK', action: 'REQUIRE_HUMAN', conditions: { riskLevels: ['HIGH', 'CRITICAL'] }, priority: 5, active: true },
];

export function evaluatePolicy(input: { amount: number; riskLevel?: string; departmentId?: string }, dbPolicies: any[] = []): PolicyRule {
  const rules: PolicyRule[] = [
    ...dbPolicies.filter((p) => p.active !== false).map((p) => ({
      code: p.code, action: p.action, priority: p.priority ?? 100, active: true,
      conditions: typeof p.conditions === 'string' ? JSON.parse(p.conditions) : (p.conditions ?? {}),
    })),
    ...DEFAULT_POLICIES,
  ].sort((a, b) => a.priority - b.priority);

  for (const r of rules) {
    const c = r.conditions;
    if (c.minAmount !== undefined && input.amount < c.minAmount) continue;
    if (c.maxAmount !== undefined && input.amount >= c.maxAmount && !(c.minAmount !== undefined && c.riskLevels)) {
      // amount-gated rules: skip when out of band (unless purely risk-gated)
      if (!c.riskLevels) continue;
    }
    if (c.riskLevels && input.riskLevel && !c.riskLevels.includes(input.riskLevel)) continue;
    if (c.departments && input.departmentId && !c.departments.includes(input.departmentId)) continue;
    // first matching rule in priority order wins; risk rules have highest priority (lowest number)
    if (c.riskLevels && !c.minAmount && !c.maxAmount) {
      if (input.riskLevel && c.riskLevels.includes(input.riskLevel)) return r;
      continue;
    }
    return r;
  }
  return { code: 'FALLBACK', action: 'REQUIRE_HUMAN', conditions: {}, priority: 999, active: true };
}
