using { procurement.db as db } from '../db/schema';

@path: '/odata/v4/audit'
service AuditService {
  @readonly entity AuditLogs as projection on db.AuditLogs;
  @readonly entity MCPToolExecutions as projection on db.MCPToolExecutions;
}
