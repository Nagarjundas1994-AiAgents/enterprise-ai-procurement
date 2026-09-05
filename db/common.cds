namespace procurement.common;

using { cuid, managed } from '@sap/cds/common';

// All tenant-sensitive entities carry tenantId (organization-based tenancy).
// Tenant is ALWAYS resolved server-side from auth context, never trusted from client.
aspect TenantAware {
  tenantId : String(64) not null;
}

aspect Auditable {
  createdByAgent : String(128);
  lastModifiedByAgent : String(128);
}

type ActorType : String enum {
  USER;
  AGENT;
  SYSTEM;
}

type PRStatus : String enum {
  DRAFT;
  SUBMITTED;
  UNDER_REVIEW;
  APPROVED;
  REJECTED;
  CONVERTED_TO_PO;
  CANCELLED;
}

type POStatus : String enum {
  DRAFT;
  PENDING_APPROVAL;
  APPROVED;
  SENT_TO_SUPPLIER;
  PARTIALLY_RECEIVED;
  FULLY_RECEIVED;
  INVOICED;
  CLOSED;
  CANCELLED;
}

type InvoiceStatus : String enum {
  DRAFT;
  SUBMITTED;
  MATCHED;
  MISMATCH;
  APPROVED;
  PAID;
  REJECTED;
  CANCELLED;
}

type PaymentStatus : String enum {
  PENDING;
  PROCESSING;
  COMPLETED;
  FAILED;
  CANCELLED;
}

type ApprovalStatus : String enum {
  PENDING;
  APPROVED;
  REJECTED;
  ESCALATED;
  CANCELLED;
}

type RiskLevel : String enum {
  LOW;
  MEDIUM;
  HIGH;
  CRITICAL;
}

type PolicyAction : String enum {
  AUTO_APPROVE;
  REQUIRE_MANAGER;
  REQUIRE_FINANCE;
  REQUIRE_HUMAN;
  DENY;
}

type ToolExecutionStatus : String enum {
  PENDING;
  RUNNING;
  SUCCESS;
  FAILED;
  DENIED;
}

type MessageRole : String enum {
  USER;
  ASSISTANT;
  TOOL;
  SYSTEM;
}
