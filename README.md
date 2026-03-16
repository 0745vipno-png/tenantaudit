TenantAudit

TenantAudit is a multi-tenant, append-only audit logging system designed for tamper-evident event recording and deterministic verification.

It provides a cryptographically linked audit trail where each event is chained using secure hashes.

Each tenant maintains its own isolated audit history.

The system is designed as a CLI-first tool for environments that require traceable and verifiable operational records.

Key Features
Multi-Tenant Isolation

Each tenant maintains a logically isolated audit history.

All operations are scoped by:

tenant_id

The system design prevents cross-tenant access.

Append-Only Audit Storage

Audit events are immutable.

The database enforces:

UPDATE → forbidden

DELETE → forbidden

This is implemented using SQLite triggers.

Audit records can only be appended.

Tamper-Evident Hash Chain

Each audit event contains:

prev_hash – hash of the previous event

event_hash – computed hash of the current event

This forms a cryptographic chain:

Event1 → Event2 → Event3 → ...

If any historical event is modified, chain verification will fail.

Run-Based Audit Sessions

Audit events are grouped into runs.

Lifecycle:

create run
    ↓
append events
    ↓
seal run

After a run is sealed:

no additional events can be appended

This guarantees that the run's audit history is finalized.

Deterministic Verification

The system can recompute the entire event chain to verify integrity.

verify run <tenant_id> <run_id>

Verification checks:

event hash integrity

prev_hash linkage

final chain hash

event count consistency

Example output:

{
  "status": "valid",
  "run_id": "...",
  "event_count": 3,
  "final_hash": "..."
}
Architecture Overview

The architecture separates command handling, business logic, data persistence, and hash-chain verification into distinct layers.

Design goals:

tenant isolation

append-only evidence storage

deterministic chain verification

CLI-first operation

Architecture Diagram

                    ┌───────────────────────┐
                    │    User / Operator    │
                    └──────────┬────────────┘
                               │
                               │ CLI commands
                               ▼
                    ┌───────────────────────┐
                    │       CLI Layer       │
                    │  tenantaudit.cli.main │
                    └──────────┬────────────┘
                               │
                               │ invokes services
                               ▼
                    ┌───────────────────────┐
                    │     Service Layer     │
                    │───────────────────────│
                    │ TenantService         │
                    │ RunService            │
                    │ AuditService          │
                    │ VerifyService         │
                    └──────────┬────────────┘
                               │
                               │ uses repositories
                               ▼
                    ┌───────────────────────┐
                    │   Repository Layer    │
                    │───────────────────────│
                    │ TenantRepository      │
                    │ RunRepository         │
                    │ EventRepository       │
                    └──────────┬────────────┘
                               │
                               │ reads / writes
                               ▼
                    ┌───────────────────────┐
                    │     SQLite Storage    │
                    │───────────────────────│
                    │ tenants               │
                    │ runs                  │
                    │ audit_events          │
                    │ exported_artifacts    │
                    └──────────┬────────────┘
                               │
                               │ chain integrity
                               ▼
                    ┌───────────────────────┐
                    │   Hash Chain Engine   │
                    │───────────────────────│
                    │ prev_hash             │
                    │ event_hash            │
                    │ final_chain_hash      │
                    └───────────────────────┘
