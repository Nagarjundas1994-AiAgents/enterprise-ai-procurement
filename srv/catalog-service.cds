using { procurement.db as db } from '../db/schema';

@path: '/odata/v4/catalog'
@odata
@mcp: 'catalog'
@mcp.instructions: 'Catalog master data and budgets. Use describe to explore entities, then query to read. Never invent IDs. All reads enforce RBAC and tenant isolation. Use checkBudget to verify funds before creating requisitions.'
service CatalogService {
  entity Users as projection on db.Users excluding { roles };
  entity Roles as projection on db.Roles;
  entity Permissions as projection on db.Permissions;
  entity Organizations as projection on db.Organizations;
  entity Departments as projection on db.Departments;
  entity Employees as projection on db.Employees;
  entity Budgets as projection on db.Budgets;
  entity BudgetConsumptions as projection on db.BudgetConsumptions;
  entity Policies as projection on db.Policies;
  entity PolicyViolations as projection on db.PolicyViolations;
  entity Notifications as projection on db.Notifications;

  /** Check department budget availability. Returns true if remaining funds cover the requested amount. */
  function checkBudget(departmentID : String, amount : Decimal) returns Boolean;
}
