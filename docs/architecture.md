TenantAudit — High-Level Architecture
TenantAudit — Multi-Tenant Audit Logging System
High-Level Architecture (v0.1)

Goal
-----
A multi-tenant, append-only audit logging platform designed for
traceability, tenant isolation, and tamper-evident verification.


────────────────────────────────────────────────────────────────────

[User / Operator]

    │
    │ CLI Commands
    │
    ▼

[CLI Layer]
  - tenant create/list/show
  - run create/seal/verify
  - event append
  - export report

    │
    │ builds tenant context
    │
    ▼

[Tenant Context Layer]
  Responsible for binding every operation to a specific tenant.

  Provides:
  - tenant_id
  - validation
  - isolation boundary

    │
    │
    ▼

[Service Layer]

  TenantService
      manage tenants

  RunService
      manage audit runs

  AuditService
      append audit events

  VerifyService
      verify chain integrity

  ExportService
      generate human-readable reports

    │
    │
    ▼

[Repository Layer]

  TenantRepository
  RunRepository
  EventRepository
  ArtifactRepository

  Responsibilities
  - translate domain operations into SQL
  - enforce tenant-scoped queries
  - prevent cross-tenant data access

    │
    │
    ▼

[Storage Layer]

  SQLite Database

  Tables
  - tenants
  - runs
  - audit_events
  - exported_artifacts

  Database Rules
  - append-only audit_events
  - append-only exported_artifacts
  - triggers block UPDATE / DELETE
  - chain integrity stored per run

    │
    │
    ▼

[Artifacts / Reports]

  Generated outputs
  - run_report.txt
  - tenant_audit_report.txt
  - verification_report.txt

  Characteristics
  - human-readable
  - hashable
  - traceable
  - tenant-scoped


────────────────────────────────────────────────────────────────────

Isolation Model
----------------

Every operation MUST include tenant context.

All queries MUST include:

    WHERE tenant_id = ?

Cross-tenant reads are strictly forbidden.


────────────────────────────────────────────────────────────────────

Audit Chain Model
------------------

Each event forms part of a cryptographic chain.

event_hash =
    SHA256(
        tenant_id
        run_id
        seq_no
        payload
        timestamp
        prev_hash
    )

Runs may be sealed with:

    final_chain_hash
    event_count


────────────────────────────────────────────────────────────────────

Design Principles
------------------

1. Multi-tenant isolation by design
2. Append-only evidence storage
3. Tamper-evident event chains
4. CLI-first operational model
5. Human-readable reporting
6. Deterministic verification