using { procurement.db as db } from '../db/schema';

// A2A agent endpoints. Each agent is a specialized service annotated with
// @agent (cap-js/agents). The orchestrator routes tasks to specialists.
// All agents call the same CAP business services -> same authZ/policy/audit.
// NOTE: @agent MUST be lowercase — the plugin checks srv.definition["@agent"].
@path: '/odata/v4/agents'
@odata
// @agent needs a STRING sub-path (see note in procurement-service.cds),
// served at /a2a/agents. @odata is kept so the OData actions stay reachable.
@agent: 'agents'
service AgentService {
  entity Agents as projection on db.Agents;
  entity AgentExecutions as projection on db.AgentExecutions;
  entity AIConversations as projection on db.AIConversations;
  entity AIMessages as projection on db.AIMessages;
  entity RiskAssessments as projection on db.RiskAssessments;

  action executeTask(agentId : String, intent : String, payload : LargeString) returns LargeString;
  action chat(conversationId : String, message : String) returns LargeString;
  action orchestrate(goal : String, payload : LargeString) returns LargeString;
  // A2A bridge to REMOTE agents (other servers). Only allowlisted agent names;
  // remote data returns as advisory intel, never bypasses authZ/policy.
  action callRemoteAgent(agentName : String, message : String) returns LargeString;
}

// --- Human-in-the-loop: orchestrator/executor/bridge can trigger downstream
// critical work (PO creation, approvals), so agents must pause for approval ---
annotate AgentService.executeTask with @agent.hitl;
annotate AgentService.orchestrate with @agent.hitl;
annotate AgentService.callRemoteAgent with @agent.hitl;
