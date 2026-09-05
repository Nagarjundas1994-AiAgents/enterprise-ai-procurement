using { procurement.db as db } from '../db/schema';

@path: '/odata/v4/invoices'
@odata
@mcp: 'invoices'
@mcp.instructions: 'Invoices, matching and payments. Use describe then query to read. Never invent IDs. All operations enforce RBAC, tenant isolation and audit. Match before approving; only APPROVED invoices can be paid (FINANCE role).'
service InvoiceService {
  entity Invoices as projection on db.Invoices;
  entity InvoiceItems as projection on db.InvoiceItems;
  entity Payments as projection on db.Payments;

  /** Three-way match of invoice against purchase order and goods receipts. */
  action matchInvoice(invoiceID : String) returns String;
  /** Approve a MATCHED or SUBMITTED invoice (audited). */
  action approveInvoice(invoiceID : String) returns String;
  /** Create a payment for an APPROVED invoice (requires FINANCE role). */
  action createPayment(invoiceID : String, amount : Decimal, method : String) returns Payments;
}
