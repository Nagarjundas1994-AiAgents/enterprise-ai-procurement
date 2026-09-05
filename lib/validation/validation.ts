import { reqError } from '../security/errors.js';

export function validateRequisition(data: any) {
  if (!data.title?.trim()) throw reqError('VALIDATION_ERROR', 'Title is required');
  if (data.totalAmount !== undefined && Number(data.totalAmount) <= 0)
    throw reqError('VALIDATION_ERROR', 'Amount must be > 0');
}

export function validatePO(pr: any, supplier: any) {
  if (!pr) throw reqError('RESOURCE_NOT_FOUND', 'Purchase requisition not found');
  if (['REJECTED', 'DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'CANCELLED'].includes(pr.status))
    throw reqError('INVALID_STATE_TRANSITION', `PO cannot be created from PR in status ${pr.status}`);
  if (!supplier?.active) throw reqError('SUPPLIER_INACTIVE', 'Supplier is inactive');
}

/** Three-way match: PO + Goods Receipt + Invoice. */
export function threeWayMatch(poItems: any[], receiptItems: any[], invItems: any[]) {
  const issues: string[] = [];
  const recvByPoItem: Record<string, number> = {};
  for (const r of receiptItems) recvByPoItem[String(r.poItem_ID ?? r.poItem)] = Number(recvByPoItem[String(r.poItem_ID ?? r.poItem)] ?? 0) + Number(r.quantity);
  for (const inv of invItems) {
    const key = String(inv.poItem_ID ?? inv.poItem ?? '');
    const po = poItems.find((p) => String(p.ID) === key);
    if (!po) { issues.push(`Invoice line ${inv.lineNo}: unknown PO item`); continue; }
    if (Number(inv.unitPrice) !== Number(po.unitPrice)) issues.push(`Invoice line ${inv.lineNo}: price mismatch ${inv.unitPrice} vs ${po.unitPrice}`);
    if (Number(inv.quantity) > Number(po.quantity)) issues.push(`Invoice line ${inv.lineNo}: quantity exceeds PO`);
    const received = recvByPoItem[key] ?? 0;
    if (Number(inv.quantity) > received) issues.push(`Invoice line ${inv.lineNo}: no goods receipt for ${inv.quantity} (received ${received})`);
  }
  return { matched: issues.length === 0, issues };
}

/** Prompt-injection defense: treat business data as DATA, strip instruction-like patterns before LLM use. */
export function sanitizeForLLM(input: unknown): string {
  const s = String(input ?? '');
  return s
    .replace(/ignore\s+(all\s+)?previous\s+instructions?/gi, '[redacted-instruction-like-text]')
    .replace(/system\s*:\s*/gi, 'system-data:')
    .slice(0, 4000);
}
