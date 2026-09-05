import { reqError } from '../security/errors.js';

export const PR_FLOW: Record<string, string[]> = {
  DRAFT: ['SUBMITTED', 'CANCELLED'],
  SUBMITTED: ['UNDER_REVIEW', 'REJECTED', 'CANCELLED'],
  UNDER_REVIEW: ['APPROVED', 'REJECTED', 'CANCELLED'],
  APPROVED: ['CONVERTED_TO_PO', 'CANCELLED'],
  REJECTED: ['DRAFT'], // explicit re-open only
  CONVERTED_TO_PO: [],
  CANCELLED: [],
};

export const PO_FLOW: Record<string, string[]> = {
  DRAFT: ['PENDING_APPROVAL', 'CANCELLED'],
  PENDING_APPROVAL: ['APPROVED', 'CANCELLED'],
  APPROVED: ['SENT_TO_SUPPLIER', 'CANCELLED'],
  SENT_TO_SUPPLIER: ['PARTIALLY_RECEIVED', 'FULLY_RECEIVED', 'CANCELLED'],
  PARTIALLY_RECEIVED: ['FULLY_RECEIVED', 'CANCELLED'],
  FULLY_RECEIVED: ['INVOICED'],
  INVOICED: ['CLOSED'],
  CLOSED: [],
  CANCELLED: [],
};

export function assertTransition(flow: Record<string, string[]>, from: string, to: string) {
  const allowed = flow[from] ?? [];
  if (!allowed.includes(to)) throw reqError('INVALID_STATE_TRANSITION', `Illegal transition ${from} -> ${to}`);
}
