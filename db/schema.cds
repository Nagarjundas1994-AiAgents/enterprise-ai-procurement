namespace procurement.db;

using { cuid, managed } from '@sap/cds/common';
using { procurement.common as c } from './common';

// ---------------------------------------------------------------------------
// Identity & Access
// ---------------------------------------------------------------------------

entity Users : cuid, managed, c.TenantAware {
  username     : String(128) not null;
  email        : String(256) not null;
  displayName  : String(256);
  active       : Boolean default true not null;
  organization : Association to Organizations;
  department   : Association to Departments;
  roles        : Association to many UserRoles on roles.user = $self;
}

entity Roles : cuid, managed {
  name        : String(64) @assert.unique not null;
  description : String(512);
  isSystem    : Boolean default false;
  permissions : Association to many RolePermissions on permissions.role = $self;
  users       : Association to many UserRoles on users.role = $self;
}

entity Permissions : cuid, managed {
  name        : String(128) @assert.unique not null;
  description : String(512);
  category    : String(64);
  roles       : Association to many RolePermissions on roles.permission = $self;
}

entity UserRoles : cuid, managed {
  user : Association to Users not null;
  role : Association to Roles not null;
}

entity RolePermissions : cuid, managed {
  role       : Association to Roles not null;
  permission : Association to Permissions not null;
}

// ---------------------------------------------------------------------------
// Organization structure
// ---------------------------------------------------------------------------

entity Organizations : cuid, managed {
  tenantId    : String(64) @assert.unique not null;
  name        : String(256) not null;
  country     : String(64);
  active      : Boolean default true;
  departments : Association to many Departments on departments.organization = $self;
  employees   : Association to many Employees on employees.organization = $self;
}

entity Departments : cuid, managed, c.TenantAware {
  code         : String(32) not null;
  name         : String(256) not null;
  organization : Association to Organizations not null;
  budget       : Association to Budgets;
  employees    : Association to many Employees on employees.department = $self;
}

entity Employees : cuid, managed, c.TenantAware {
  employeeId   : String(64) not null;
  user         : Association to Users;
  organization : Association to Organizations not null;
  department   : Association to Departments;
  manager      : Association to Employees;
  jobTitle     : String(128);
  active       : Boolean default true;
}

// ---------------------------------------------------------------------------
// Master data: suppliers & materials
// ---------------------------------------------------------------------------

entity Suppliers : cuid, managed, c.TenantAware {
  supplierId   : String(64) not null;
  name         : String(256) not null;
  country      : String(64);
  taxId        : String(64);
  active       : Boolean default true not null;
  riskScore    : Integer default 0;
  riskLevel    : c.RiskLevel default #LOW;
  onTimeRate   : Decimal(5, 2) default 100.0;
  disputeCount : Integer default 0;
  totalSpend   : Decimal(18, 2) default 0;
  contacts     : Composition of many SupplierContacts on contacts.supplier = $self;
  purchaseOrders : Association to many PurchaseOrders on purchaseOrders.supplier = $self;
}

entity SupplierContacts : cuid, managed {
  supplier : Association to Suppliers not null;
  name     : String(256) not null;
  email    : String(256);
  phone    : String(64);
  role     : String(128);
}

entity MaterialCategories : cuid, managed {
  code        : String(32) @assert.unique not null;
  name        : String(256) not null;
  description : String(1024);
}

entity Materials : cuid, managed, c.TenantAware {
  materialId : String(64) not null;
  name       : String(256) not null;
  category   : Association to MaterialCategories;
  unit       : String(16) default 'EA';
  unitPrice  : Decimal(18, 2) not null;
  currency   : String(3) default 'INR';
  active     : Boolean default true;
}

// ---------------------------------------------------------------------------
// Procurement: requisitions, approvals, orders, receipts, invoices, payments
// ---------------------------------------------------------------------------

entity PurchaseRequisitions : cuid, managed, c.TenantAware, c.Auditable {
  requisitionNo : String(32) @assert.unique not null;
  title         : String(256) not null;
  description   : String(2048);
  requester     : Association to Users not null;
  department    : Association to Departments not null;
  status        : c.PRStatus default #DRAFT not null;
  totalAmount   : Decimal(18, 2) default 0 not null;
  currency      : String(3) default 'INR';
  priority      : String(16) default 'NORMAL';
  version       : Integer default 1 not null; // optimistic concurrency
  items         : Composition of many PurchaseRequisitionItems on items.requisition = $self;
  approvals     : Association to many Approvals on approvals.requisition = $self;
  purchaseOrders : Association to many PurchaseOrders on purchaseOrders.requisition = $self;
}

entity PurchaseRequisitionItems : cuid {
  requisition : Association to PurchaseRequisitions not null;
  lineNo      : Integer not null;
  material    : Association to Materials;
  description : String(1024) not null;
  quantity    : Decimal(15, 3) not null;
  unit        : String(16) default 'EA';
  unitPrice   : Decimal(18, 2) not null;
  currency    : String(3) default 'INR';
  lineAmount  : Decimal(18, 2);
}

entity Approvals : cuid, managed, c.TenantAware {
  requisition : Association to PurchaseRequisitions not null;
  stepNo      : Integer not null;
  approver    : Association to Users;
  status      : c.ApprovalStatus default #PENDING not null;
  comment     : String(2048);
  decidedAt   : DateTime;
  steps       : Composition of many ApprovalSteps on steps.approval = $self;
}

entity ApprovalSteps : cuid, managed {
  approval  : Association to Approvals not null;
  stepNo    : Integer not null;
  actor     : Association to Users;
  action    : String(32);
  comment   : String(2048);
  createdAt : DateTime;
}

entity PurchaseOrders : cuid, managed, c.TenantAware, c.Auditable {
  orderNo       : String(32) @assert.unique not null;
  requisition   : Association to PurchaseRequisitions;
  supplier      : Association to Suppliers not null;
  status        : c.POStatus default #DRAFT not null;
  totalAmount   : Decimal(18, 2) default 0 not null;
  currency      : String(3) default 'INR';
  version       : Integer default 1 not null;
  orderedAt     : DateTime;
  expectedAt    : Date;
  createdByUser : Association to Users;
  items         : Composition of many PurchaseOrderItems on items.purchaseOrder = $self;
  receipts      : Association to many GoodsReceipts on receipts.purchaseOrder = $self;
  invoices      : Association to many Invoices on invoices.purchaseOrder = $self;
}

entity PurchaseOrderItems : cuid {
  purchaseOrder : Association to PurchaseOrders not null;
  lineNo        : Integer not null;
  material      : Association to Materials;
  description   : String(1024) not null;
  quantity      : Decimal(15, 3) not null;
  unit          : String(16) default 'EA';
  unitPrice     : Decimal(18, 2) not null;
  currency      : String(3) default 'INR';
  lineAmount    : Decimal(18, 2);
  receivedQty   : Decimal(15, 3) default 0;
  invoicedQty   : Decimal(15, 3) default 0;
}

entity GoodsReceipts : cuid, managed, c.TenantAware {
  receiptNo     : String(32) @assert.unique not null;
  purchaseOrder : Association to PurchaseOrders not null;
  receivedAt    : DateTime;
  receivedBy    : Association to Users;
  note          : String(2048);
  items         : Composition of many GoodsReceiptItems on items.receipt = $self;
}

entity GoodsReceiptItems : cuid {
  receipt  : Association to GoodsReceipts not null;
  poItem   : Association to PurchaseOrderItems not null;
  quantity : Decimal(15, 3) not null;
}

entity Invoices : cuid, managed, c.TenantAware, c.Auditable {
  invoiceNo     : String(64) not null;
  purchaseOrder : Association to PurchaseOrders;
  supplier      : Association to Suppliers not null;
  status        : c.InvoiceStatus default #DRAFT not null;
  totalAmount   : Decimal(18, 2) not null;
  currency      : String(3) default 'INR';
  invoiceDate   : Date;
  dueDate       : Date;
  matchResult   : String(32);
  matchDetails  : LargeString;
  items         : Composition of many InvoiceItems on items.invoice = $self;
  payments      : Association to many Payments on payments.invoice = $self;
}

entity InvoiceItems : cuid {
  invoice     : Association to Invoices not null;
  lineNo      : Integer not null;
  poItem      : Association to PurchaseOrderItems;
  description : String(1024) not null;
  quantity    : Decimal(15, 3) not null;
  unitPrice   : Decimal(18, 2) not null;
  lineAmount  : Decimal(18, 2);
}

entity Payments : cuid, managed, c.TenantAware {
  paymentNo : String(32) @assert.unique not null;
  invoice   : Association to Invoices not null;
  amount    : Decimal(18, 2) not null;
  currency  : String(3) default 'INR';
  status    : c.PaymentStatus default #PENDING not null;
  paidAt    : DateTime;
  method    : String(32);
}

// ---------------------------------------------------------------------------
// Budgets
// ---------------------------------------------------------------------------

entity Budgets : cuid, managed, c.TenantAware {
  code          : String(64) not null;
  department    : Association to Departments;
  fiscalYear    : Integer not null;
  totalAmount   : Decimal(18, 2) not null;
  committed     : Decimal(18, 2) default 0;
  consumed      : Decimal(18, 2) default 0;
  currency      : String(3) default 'INR';
  consumptions  : Association to many BudgetConsumptions on consumptions.budget = $self;
}

entity BudgetConsumptions : cuid, managed, c.TenantAware {
  budget      : Association to Budgets not null;
  requisition : Association to PurchaseRequisitions;
  order       : Association to PurchaseOrders;
  amount      : Decimal(18, 2) not null;
  type        : String(32);
}

// ---------------------------------------------------------------------------
// Workflow / notifications
// ---------------------------------------------------------------------------

entity Workflows : cuid, managed, c.TenantAware {
  code        : String(64) not null;
  name        : String(256) not null;
  entityType  : String(64) not null;
  active      : Boolean default true;
  tasks       : Composition of many WorkflowTasks on tasks.workflow = $self;
}

entity WorkflowTasks : cuid, managed, c.TenantAware {
  workflow   : Association to Workflows not null;
  entityId   : String(64) not null;
  entityType : String(64) not null;
  assignee   : Association to Users;
  status     : String(32) default 'OPEN';
  dueAt      : DateTime;
  payload    : LargeString;
}

entity Notifications : cuid, managed, c.TenantAware {
  recipient : Association to Users not null;
  title     : String(256) not null;
  body      : LargeString;
  channel   : String(32) default 'INAPP';
  read      : Boolean default false;
  relatedEntity : String(128);
  relatedId     : String(64);
}

// ---------------------------------------------------------------------------
// Audit
// ---------------------------------------------------------------------------

entity AuditLogs : cuid, managed {
  timestamp     : DateTime;
  tenantId      : String(64);
  actorType     : c.ActorType not null;
  actorId       : String(128) not null;
  userId        : String(128);
  agentId       : String(128);
  delegatedUserId : String(128);
  action        : String(128) not null;
  entity        : String(128);
  entityId      : String(128);
  oldValue      : LargeString;
  newValue      : LargeString;
  result        : String(32) default 'SUCCESS';
  correlationId : String(64);
  requestId     : String(64);
  ipAddress     : String(64);
}

// ---------------------------------------------------------------------------
// Agents / MCP / AI
// ---------------------------------------------------------------------------

entity Agents : cuid, managed, c.TenantAware {
  agentId       : String(128) @assert.unique not null;
  name          : String(256) not null;
  kind          : String(64) not null; // PROCUREMENT, APPROVAL, RISK, INVOICE, BUDGET, AUDIT, ORCHESTRATOR
  owner         : Association to Users;
  active        : Boolean default true;
  allowedTools  : LargeString;   // JSON array
  allowedEntities : LargeString; // JSON array
  allowedActions  : LargeString; // JSON array
  maxAutoApproveAmount : Decimal(18, 2) default 50000;
  permissions   : Association to many AgentPermissions on permissions.agent = $self;
  toolGrants    : Association to many AgentToolPermissions on toolGrants.agent = $self;
  executions    : Association to many AgentExecutions on executions.agent = $self;
}

entity AgentPermissions : cuid, managed {
  agent      : Association to Agents not null;
  permission : Association to Permissions not null;
}

entity AgentToolPermissions : cuid, managed, c.TenantAware {
  agent      : Association to Agents not null;
  toolName   : String(128) not null;
  allowed    : Boolean default true;
  maxAmount  : Decimal(18, 2);
}

entity AgentExecutions : cuid, managed {
  agent       : Association to Agents;
  user        : Association to Users;
  tenantId    : String(64);
  conversation : Association to AIConversations;
  toolName    : String(128);
  input       : LargeString;
  output      : LargeString;
  status      : c.ToolExecutionStatus default #PENDING;
  startedAt   : DateTime;
  completedAt : DateTime;
  error       : LargeString;
  authorizationDecision : String(32);
  correlationId : String(64);
}

entity MCPTools : cuid, managed {
  name               : String(128) @assert.unique not null;
  description        : String(1024) not null;
  inputSchema        : LargeString;
  outputSchema       : LargeString;
  requiredPermission : String(128) not null;
  allowedRoles       : LargeString; // JSON
  rateLimitPerMin    : Integer default 60;
  active             : Boolean default true;
  executions         : Association to many MCPToolExecutions on executions.tool = $self;
}

entity MCPToolExecutions : cuid, managed {
  tool        : Association to MCPTools not null;
  tenantId    : String(64);
  actorType   : c.ActorType not null;
  actorId     : String(128) not null;
  agentId     : String(128);
  input       : LargeString;
  output      : LargeString;
  status      : c.ToolExecutionStatus default #PENDING;
  error       : LargeString;
  correlationId : String(64);
  durationMs  : Integer;
}

entity AIConversations : cuid, managed {
  conversationId : String(64) @assert.unique not null;
  user           : Association to Users;
  agent          : Association to Agents;
  tenantId       : String(64);
  title          : String(256);
  messages       : Composition of many AIMessages on messages.conversation = $self;
}

entity AIMessages : cuid {
  conversation : Association to AIConversations not null;
  role         : c.MessageRole not null;
  content      : LargeString not null;
  toolCalls    : LargeString;
  createdAt    : DateTime;
}

// ---------------------------------------------------------------------------
// Risk & policy
// ---------------------------------------------------------------------------

entity RiskAssessments : cuid, managed, c.TenantAware {
  entityType  : String(64) not null;
  entityId    : String(64) not null;
  riskScore   : Integer not null;
  riskLevel   : c.RiskLevel not null;
  reasons     : LargeString;
  recommendation : String(1024);
  assessedBy  : String(128);
  assessedAt  : DateTime;
}

entity Policies : cuid, managed, c.TenantAware {
  code        : String(128) not null;
  name        : String(256) not null;
  description : String(2048);
  conditions  : LargeString not null; // JSON
  action      : c.PolicyAction not null;
  priority    : Integer default 100;
  active      : Boolean default true;
  violations  : Association to many PolicyViolations on violations.policy = $self;
}

entity PolicyViolations : cuid, managed, c.TenantAware {
  policy     : Association to Policies not null;
  entityType : String(64) not null;
  entityId   : String(64) not null;
  detail     : LargeString;
  resolved   : Boolean default false;
}
