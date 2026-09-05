using { procurement.db as db } from '../db/schema';

@path: '/odata/v4/approval'
@odata
@mcp: 'approvals'
@mcp.instructions: 'Approval workflows and tasks. Use describe then query to read pending approvals. Never invent IDs. All operations enforce RBAC, tenant isolation and audit. Decisions go through decideApproval.'
service ApprovalService {
  entity Approvals as projection on db.Approvals;
  entity ApprovalSteps as projection on db.ApprovalSteps;
  entity Workflows as projection on db.Workflows;
  entity WorkflowTasks as projection on db.WorkflowTasks;

  /** Decide an approval (APPROVE or REJECT) with a comment. Audited, single-decision only. */
  action decideApproval(approvalID : String, decision : String, comment : String) returns String;
}
