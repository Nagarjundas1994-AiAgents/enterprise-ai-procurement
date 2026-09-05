using { procurement.db as db } from '../db/schema';

// A2A agent endpoints. Each agent is a specialized service annotated with
// @Agent (cap-js/agents, alpha). The orchestrator routes tasks to specialists.
// All agents call the same CAP business services -> same authZ/policy/audit.
@path: '/odata/v4/agents'
@Agent
service AgentService {
  entity Agents as projection on db.Agents;
  entity AgentExecutions as projection on db.AgentExecutions;
  entity AIConversations as projection on db.AIConversations;
  entity AIMessages as projection on db.AIMessages;
  entity RiskAssessments as projection on db.RiskAssessments;

  action executeTask(agentId : String, intent : String, payload : LargeString) returns LargeString;
  action chat(conversationId : String, message : String) returns LargeString;
  action orchestrate(goal : String, payload : LargeString) returns LargeString;
}
