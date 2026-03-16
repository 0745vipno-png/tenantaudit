TenantAudit — System Data Flow Architecture
TenantAudit — System Data Flow
v0.1

Goal
-----
Describe how data moves through the system during core operations.


────────────────────────────────────────────────────────────────────

                    System Actors


        [User / Operator]

                │
                │ CLI Commands
                ▼


────────────────────────────────────────────────────────────────────

                    CLI Interface


        tenantaudit tenant create
        tenantaudit run create
        tenantaudit event append
        tenantaudit run seal
        tenantaudit run verify
        tenantaudit export report


CLI Responsibilities

    - parse arguments
    - validate command syntax
    - resolve tenant_id
    - create TenantContext


                │
                │
                ▼


────────────────────────────────────────────────────────────────────

                Tenant Context Creation


        TenantContext
        ─────────────────────
        tenant_id


Example

        TenantContext("acme")


Context travels through all operations.


                │
                │
                ▼


────────────────────────────────────────────────────────────────────

                    Service Layer


Services orchestrate the system behavior.


        TenantService
        RunService
        AuditService
        VerifyService
        ExportService


Service Responsibilities

    - enforce business rules
    - validate tenant ownership
    - enforce run state
    - coordinate repositories


                │
                │
                ▼


────────────────────────────────────────────────────────────────────

                    Repository Layer


Repositories perform database access.


        TenantRepository
        RunRepository
        EventRepository
        ArtifactRepository


Responsibilities

    - execute SQL queries
    - enforce tenant-scoped reads
    - enforce tenant-scoped writes


                │
                │
                ▼


────────────────────────────────────────────────────────────────────

                    Database Layer


        SQLite Database


Tables

        tenants
        runs
        audit_events
        exported_artifacts


Database Responsibilities

    - enforce append-only rules
    - maintain referential integrity
    - persist audit chain


                │
                │
                ▼


────────────────────────────────────────────────────────────────────

                    Artifacts Layer


Generated outputs


        run_report.txt
        verification_report.txt
        tenant_report.txt


Artifacts Characteristics

        human readable
        reproducible
        hashable evidence
核心操作的 Data Flow

接下來是 三個最重要的操作流程。

Flow 1 — Append Audit Event
User
 │
 │ CLI command
 │
 ▼

tenantaudit event append
    --tenant acme
    --run-id R1


CLI
 │
 │ build TenantContext
 ▼

TenantContext(acme)

 │
 ▼

AuditService.append_event()

 │
 │ validate run ownership
 │
 ▼

RunRepository.get_run()

 │
 ▼

EventRepository.get_last_event()

 │
 ▼

Compute

    seq_no
    prev_hash
    event_hash

 │
 ▼

EventRepository.insert_event()

 │
 ▼

Database

    audit_events (append)

結果：

New event added to chain
Flow 2 — Seal Run
User
 │
 ▼

tenantaudit run seal
    --tenant acme
    --run-id R1


CLI
 │
 ▼

TenantContext(acme)

 │
 ▼

RunService.seal_run()

 │
 ▼

EventRepository.get_last_event()

 │
 ▼

Compute

    final_chain_hash
    event_count

 │
 ▼

RunRepository.update_run()

 │
 ▼

Database

    runs.status = sealed

結果：

run becomes immutable
Flow 3 — Verify Audit Chain
User
 │
 ▼

tenantaudit run verify
    --tenant acme
    --run-id R1


CLI
 │
 ▼

TenantContext(acme)

 │
 ▼

VerifyService.verify_run()

 │
 ▼

EventRepository.get_events()

 │
 ▼

Recompute chain

    verify prev_hash
    recompute event_hash

 │
 ▼

Compare

    last_hash == final_chain_hash

 │
 ▼

Generate

    verification report

輸出：

CHAIN VALID
or
CHAIN BROKEN
Tenant Isolation in Data Flow

所有 flow 都包含：

TenantContext

並且所有 query 都是：

WHERE tenant_id = ?

這確保：

tenant A
cannot see
tenant B
Data Flow Summary

系統資料流固定為：

User
 ↓
CLI
 ↓
TenantContext
 ↓
Service Layer
 ↓
Repository Layer
 ↓
Database
 ↓
Artifacts / Reports

flow 永遠不會被繞過。