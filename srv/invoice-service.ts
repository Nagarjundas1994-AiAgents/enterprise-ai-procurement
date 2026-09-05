import { randomUUID } from 'node:crypto';
import cds from '@sap/cds';
import { authenticateRequest } from '../lib/auth/authentication.js';
import { AuthorizationService } from '../lib/authorization/authorization.js';
import { PERMISSIONS } from '../lib/auth/rbac.js';
import { threeWayMatch } from '../lib/validation/validation.js';
import { writeAudit } from '../lib/audit/audit.js';
import { toHttpError } from '../lib/security/errors.js';

async function ctxOf(req: any) {
  const { ctx } = await authenticateRequest(req.http?.req ?? req);
  AuthorizationService.requireAuth(ctx);
  return ctx;
}

export default class InvoiceService extends (cds.ApplicationService as any) {
  async init() {
    const { Invoices } = this.entities;
    this.before('READ', Invoices, async (req: any) => {
      const ctx = await ctxOf(req);
      AuthorizationService.requirePermission(ctx, PERMISSIONS.READ_INVOICE);
      req.query.where({ tenantId: ctx.tenantId });
    });
    this.before('CREATE', Invoices, async (req: any) => {
      const ctx = await ctxOf(req);
      AuthorizationService.requirePermission(ctx, PERMISSIONS.CREATE_INVOICE);
      req.data.tenantId = ctx.tenantId;
      req.data.invoiceNo = req.data.invoiceNo ?? `INV-${Date.now().toString().slice(-6)}`;
      if (Number(req.data.totalAmount) <= 0) throw Object.assign(new Error('Amount must be > 0'), { code: 'VALIDATION_ERROR', status: 400 });
    });
    this.on('matchInvoice', async (req: any) => {
      try {
        const ctx = await ctxOf(req);
        AuthorizationService.requirePermission(ctx, PERMISSIONS.READ_INVOICE);
        const tx = cds.tx(req);
        const inv: any = await tx.run(SELECT.one.from('procurement.db.Invoices').where({ ID: req.data.invoiceID, tenantId: ctx.tenantId }));
        if (!inv) throw Object.assign(new Error('Not found'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
        const poItems: any[] = inv.purchaseOrder_ID ? await tx.read('procurement.db.PurchaseOrderItems').where({ purchaseOrder_ID: inv.purchaseOrder_ID }) : [];
        const receipts: any[] = inv.purchaseOrder_ID ? await tx.read('procurement.db.GoodsReceipts').where({ purchaseOrder_ID: inv.purchaseOrder_ID }) : [];
        let receiptItems: any[] = [];
        for (const r of receipts) receiptItems.push(...(await tx.read('procurement.db.GoodsReceiptItems').where({ receipt_ID: r.ID })));
        const invItems: any[] = await tx.read('procurement.db.InvoiceItems').where({ invoice_ID: inv.ID });
        const { matched, issues } = threeWayMatch(poItems, receiptItems, invItems);
        await tx.update('procurement.db.Invoices').set({ status: matched ? 'MATCHED' : 'MISMATCH', matchResult: matched ? 'MATCHED' : 'MISMATCH', matchDetails: JSON.stringify(issues).slice(0, 4000) }).where({ ID: inv.ID });
        await writeAudit(tx, ctx, { action: 'INVOICE_MATCHED', entity: 'Invoices', entityId: inv.ID, newValue: { matched, issues } });
        return matched ? 'MATCHED' : `MISMATCH: ${issues.join('; ')}`;
      } catch (e) { req.reject(toHttpError(e)); }
    });
    this.on('approveInvoice', async (req: any) => {
      try {
        const ctx = await ctxOf(req);
        AuthorizationService.requirePermission(ctx, PERMISSIONS.APPROVE_INVOICE);
        const tx = cds.tx(req);
        const inv: any = await tx.run(SELECT.one.from('procurement.db.Invoices').where({ ID: req.data.invoiceID, tenantId: ctx.tenantId }).forUpdate());
        if (!inv) throw Object.assign(new Error('Not found'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
        if (!['MATCHED', 'SUBMITTED'].includes(inv.status)) throw Object.assign(new Error(`Cannot approve from ${inv.status}`), { code: 'INVALID_STATE_TRANSITION', status: 409 });
        await tx.update('procurement.db.Invoices').set({ status: 'APPROVED' }).where({ ID: inv.ID });
        await writeAudit(tx, ctx, { action: 'INVOICE_APPROVED', entity: 'Invoices', entityId: inv.ID, oldValue: inv.status, newValue: 'APPROVED' });
        return 'APPROVED';
      } catch (e) { req.reject(toHttpError(e)); }
    });
    this.on('createPayment', async (req: any) => {
      try {
        const ctx = await ctxOf(req);
        AuthorizationService.requirePermission(ctx, PERMISSIONS.APPROVE_INVOICE);
        if (!ctx.roles.includes('FINANCE') && !ctx.roles.includes('ADMIN'))
          throw Object.assign(new Error('FINANCE role required'), { code: 'FORBIDDEN', status: 403 });
        const tx = cds.tx(req);
        const inv: any = await tx.run(SELECT.one.from('procurement.db.Invoices').where({ ID: req.data.invoiceID, tenantId: ctx.tenantId }));
        if (!inv || inv.status !== 'APPROVED') throw Object.assign(new Error('Invoice must be APPROVED'), { code: 'INVALID_STATE_TRANSITION', status: 409 });
        const payId = randomUUID();
        await tx.run(INSERT.into('procurement.db.Payments').entries({
          ID: payId,
          paymentNo: `PAY-${Date.now().toString().slice(-6)}`, invoice_ID: inv.ID,
          tenantId: ctx.tenantId, amount: req.data.amount, currency: 'INR', status: 'COMPLETED',
          paidAt: new Date().toISOString(), method: req.data.method ?? 'BANK',
        }));
        // INSERT returns the row on SQLite but [] on PostgreSQL — re-read by known ID.
        const pay: any = await tx.run(SELECT.one.from('procurement.db.Payments').where({ ID: payId }));
        await tx.update('procurement.db.Invoices').set({ status: 'PAID' }).where({ ID: inv.ID });
        await writeAudit(tx, ctx, { action: 'PAYMENT_CREATED', entity: 'Payments', newValue: { invoice: inv.invoiceNo, amount: req.data.amount } });
        return pay;
      } catch (e) { req.reject(toHttpError(e)); }
    });
    return super.init();
  }
}
