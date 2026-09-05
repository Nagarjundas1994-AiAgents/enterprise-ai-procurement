using { procurement.db as db } from '../db/schema';

// MCP-exposed business capabilities. Served via @mcp protocol adapter
// (runtime MCP business interface). Distinct from @cap-js/mcp-server which
// is only a development-time assistant. See README + AGENTS.md.
@path: '/odata/v4/mcp'
@odata
@mcp: 'procurement'
@mcp.instructions: 'Use search tools to explore procurement data. Never invent IDs. All tools enforce RBAC, tenant isolation and policy checks.'
service MCPService {
  entity PurchaseRequisitions as projection on db.PurchaseRequisitions;
  entity PurchaseOrders as projection on db.PurchaseOrders;
  entity Suppliers as projection on db.Suppliers;
  entity Invoices as projection on db.Invoices;
  entity Approvals as projection on db.Approvals;
  entity RiskAssessments as projection on db.RiskAssessments;

  @mcp.description: 'Search purchase requisitions with optional status filter'
  function searchPurchaseRequisitions(status : String, search : String, top : Integer) returns many PurchaseRequisitions;

  @mcp.description: 'Get a single purchase requisition with items'
  function getPurchaseRequisition(ID : String) returns PurchaseRequisitions;

  @mcp.description: 'Create a purchase requisition (requires CREATE_PURCHASE_REQUISITION)'
  action createPurchaseRequisition(title : String, description : String, departmentID : String, totalAmount : Decimal) returns PurchaseRequisitions;

  @mcp.description: 'Search purchase orders'
  function searchPurchaseOrders(status : String, search : String) returns many PurchaseOrders;

  @mcp.description: 'Get a single purchase order'
  function getPurchaseOrder(ID : String) returns PurchaseOrders;

  @mcp.description: 'Create a purchase order from an approved requisition (requires CREATE_PURCHASE_ORDER + policy check)'
  action createPurchaseOrder(requisitionID : String, supplierID : String) returns PurchaseOrders;

  @mcp.description: 'Search suppliers'
  function searchSuppliers(search : String) returns many Suppliers;

  @mcp.description: 'Get supplier details'
  function getSupplier(ID : String) returns Suppliers;

  @mcp.description: 'Check department budget availability'
  function checkBudget(departmentID : String, amount : Decimal) returns Boolean;

  @mcp.description: 'Get invoice status'
  function getInvoiceStatus(ID : String) returns Invoices;

  @mcp.description: 'Get approval status for a requisition'
  function getApprovalStatus(requisitionID : String) returns many Approvals;

  @mcp.description: 'Assess procurement risk for a requisition'
  function getProcurementRisk(requisitionID : String) returns RiskAssessments;

  @mcp.description: 'Submit a requisition for approval'
  action submitForApproval(requisitionID : String) returns String;
}
