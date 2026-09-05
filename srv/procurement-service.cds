using { procurement.db as db } from '../db/schema';

@path: '/odata/v4/procurement'
@odata
@mcp: 'procurement-ops'
@mcp.instructions: 'Purchase requisitions and orders. Use describe then query to read. Never invent IDs. All operations enforce RBAC, tenant isolation, policy gates and audit. State-changing work goes through unbound actions (submit, approve, reject, convert).'
service ProcurementService {

  @odata.draft.enabled: false
  entity PurchaseRequisitions as projection on db.PurchaseRequisitions;
  entity PurchaseRequisitionItems as projection on db.PurchaseRequisitionItems;
  entity PurchaseOrders as projection on db.PurchaseOrders;
  entity PurchaseOrderItems as projection on db.PurchaseOrderItems;
  entity GoodsReceipts as projection on db.GoodsReceipts;
  entity GoodsReceiptItems as projection on db.GoodsReceiptItems;

  /** Submit a DRAFT requisition for approval. */
  action submitRequisition(ID : String) returns String;
  /** Approve a submitted requisition (manager approval, audited). */
  action approveRequisition(ID : String, comment : String) returns String;
  /** Reject a requisition with a reason (audited). */
  action rejectRequisition(ID : String, comment : String) returns String;
  /** Convert an approved requisition into a purchase order (budget + policy gated). */
  action convertToPurchaseOrder(requisitionID : String, supplierID : String) returns PurchaseOrders;
}
