using { procurement.db as db } from '../db/schema';

@path: '/odata/v4/approval'
@odata
@mcp: 'approvals'
@mcp.instructions: 'Approval workflows and tasks. Use describe then query to read pending approvals. Never invent IDs. All operations enforce RBAC, tenant isolation and audit. Decisions go through decideApproval.'
// A2A agentification via @cap-js/agents, served at /a2a/approval
// (string value required — see note in procurement-service.cds).
@agent: 'approval'
service ApprovalService {
  entity Approvals as projection on db.Approvals;
  entity ApprovalSteps as projection on db.ApprovalSteps;
  entity Workflows as projection on db.Workflows;
  entity WorkflowTasks as projection on db.WorkflowTasks;

  /** Decide an approval (APPROVE or REJECT) with a comment. Audited, single-decision only. */
  action decideApproval(approvalID : String, decision : String, comment : String) returns String;
}

// --- Human-in-the-loop: approval decisions always need a human ---
annotate ApprovalService.decideApproval with @agent.hitl;
