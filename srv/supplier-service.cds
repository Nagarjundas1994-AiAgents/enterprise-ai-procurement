using { procurement.db as db } from '../db/schema';

@path: '/odata/v4/suppliers'
@odata
@mcp: 'suppliers'
@mcp.instructions: 'Supplier master data and materials. Use describe then query to read. Never invent IDs. All reads enforce RBAC and tenant isolation. Use assessSupplierRisk before selecting a supplier.'
// A2A agentification via @cap-js/agents, served at /a2a/suppliers
// (read-only tools, no HITL needed; string value required — see procurement-service.cds).
@agent: 'suppliers'
service SupplierService {
  entity Suppliers as projection on db.Suppliers;
  entity SupplierContacts as projection on db.SupplierContacts;
  entity Materials as projection on db.Materials;
  entity MaterialCategories as projection on db.MaterialCategories;

  /** Assess risk for a supplier (disputes, on-time rate). Returns risk score, level and recommendation. */
  function assessSupplierRisk(supplierID : String) returns LargeString;
}
