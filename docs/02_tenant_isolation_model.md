TenantAudit — Tenant Isolation Architecture
TenantAudit — Tenant Isolation Architecture
v0.1

Goal
-----
Ensure strict data isolation between tenants by enforcing tenant context
through every layer of the system.


────────────────────────────────────────────────────────────────────

                [User / Operator]
                        │
                        │ CLI command
                        ▼
               tenantaudit run create
               tenantaudit event append
               tenantaudit run verify


────────────────────────────────────────────────────────────────────

                    [CLI Layer]

Responsible for:

- Parsing command arguments
- Resolving tenant identifier
- Creating TenantContext

Example:

    tenantaudit event append \
        --tenant acme \
        --run-id RUN123

Produces:

    TenantContext(tenant_id="acme")


                        │
                        │ inject context
                        ▼


────────────────────────────────────────────────────────────────────

                [Tenant Context Layer]

Core isolation boundary.

Structure:

    TenantContext
        tenant_id

Rules:

- Every operation MUST include TenantContext
- Services MUST NOT operate without context
- Context cannot be mutated during execution


                        │
                        │
                        ▼


────────────────────────────────────────────────────────────────────

                    [Service Layer]

Business logic always runs inside tenant scope.

Services include:

    TenantService
    RunService
    AuditService
    VerifyService
    ExportService


Example operation flow:

    AuditService.append_event(ctx, run_id, payload)


Responsibilities:

- Validate run belongs to tenant
- Reject cross-tenant operations
- Enforce run state rules
- Pass tenant_id to repository


                        │
                        │
                        ▼


────────────────────────────────────────────────────────────────────

                  [Repository Layer]

Repository layer translates domain logic into SQL queries.

Repositories:

    TenantRepository
    RunRepository
    EventRepository
    ArtifactRepository


CRITICAL RULE:

Every query MUST include tenant scope.


Example (SAFE):

    SELECT *
    FROM runs
    WHERE run_id = ?
      AND tenant_id = ?


Example (UNSAFE):

    SELECT *
    FROM runs
    WHERE run_id = ?


Repository layer guarantees:

- tenant-scoped queries
- prevention of cross-tenant reads
- prevention of cross-tenant writes


                        │
                        │
                        ▼


────────────────────────────────────────────────────────────────────

                    [Database Layer]

SQLite storage.


Tables:

    tenants
    runs
    audit_events
    exported_artifacts


Isolation strategy:

    Logical isolation via tenant_id column


Example structure:

    audit_events

        tenant_id
        run_id
        seq_no
        payload_json
        event_hash


Append-only enforcement:

    audit_events
        UPDATE → blocked
        DELETE → blocked

via database triggers.


────────────────────────────────────────────────────────────────────

                    Isolation Flow


    User Command
         │
         ▼
    CLI resolves tenant
         │
         ▼
    TenantContext created
         │
         ▼
    Service validates tenant ownership
         │
         ▼
    Repository executes tenant-scoped query
         │
         ▼
    Database returns only tenant data


────────────────────────────────────────────────────────────────────

                Cross-Tenant Protection


The system prevents the following violations:


Case 1 — Reading another tenant's run

    tenant A tries to read run belonging to tenant B

Result:

    repository query returns nothing
    service raises error


Case 2 — Writing event to another tenant's run

    tenant A attempts to append event to run B

Result:

    service validation fails
    operation rejected


Case 3 — Exporting cross-tenant data

    tenant A attempts global export

Result:

    export service enforces tenant scope


────────────────────────────────────────────────────────────────────

                Security Assumptions


The system assumes:

- tenant_id is always explicitly provided
- services never bypass repository layer
- repository layer never executes tenant-less queries


Isolation is enforced at three levels:

    1. Context enforcement
    2. Service validation
    3. SQL query scoping


Breaking any layer would require code modification,
not just malformed user input.
這張圖的核心價值

這張 Tenant Isolation Architecture 其實在展示三層保護：

層級	作用
Context	所有操作綁 tenant
Service	驗證 run / tenant 關係
Repository	SQL 強制 tenant filter

也就是：

User
 ↓
Context enforcement
 ↓
Service validation
 ↓
SQL tenant filter

三層同時存在，才算 真正的 multi-tenant isolation。