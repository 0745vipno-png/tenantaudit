TenantAudit — Data Model Architecture
v0.1

Goal
-----
Define the relational model for a multi-tenant, append-only
audit logging system with verifiable event chains.


────────────────────────────────────────────────────────────────────

                           [tenants]


        tenants
        ─────────────────────────────
        tenant_id        TEXT  PK
        tenant_name      TEXT  UNIQUE
        status           TEXT
        created_at       TEXT


        Example

        tenant_id    tenant_name
        ----------   -----------
        t_acme       acme
        t_globex     globex


Purpose

    Root entity for tenant isolation.

Every other table references tenant_id.



────────────────────────────────────────────────────────────────────

                              │
                              │ 1:N
                              ▼


                           [runs]


        runs
        ─────────────────────────────────────────
        run_id             TEXT  PK
        tenant_id          TEXT  FK → tenants
        status             TEXT  (open / sealed)

        started_at         TEXT
        sealed_at          TEXT

        final_chain_hash   TEXT
        event_count        INTEGER


Example

        run_id     tenant_id   status
        -------    ---------   ------
        r001       t_acme      open
        r002       t_acme      sealed
        r003       t_globex    sealed


Purpose

    Logical grouping of audit events.

A run represents a single audit session
or operation batch.

When sealed:

    final_chain_hash becomes immutable.



────────────────────────────────────────────────────────────────────

                              │
                              │ 1:N
                              ▼


                        [audit_events]


        audit_events
        ────────────────────────────────────────────────
        event_id        TEXT  PK

        tenant_id       TEXT  FK → tenants
        run_id          TEXT  FK → runs

        seq_no          INTEGER

        event_type      TEXT
        payload_json    TEXT

        occurred_at     TEXT

        prev_hash       TEXT
        event_hash      TEXT


Example

        event_id   run_id   seq   prev_hash   event_hash
        --------   ------   ---   ---------   ----------
        e1         r001     1     NULL        H1
        e2         r001     2     H1          H2
        e3         r001     3     H2          H3


Purpose

    Immutable audit log records.

Key properties

    append-only
    ordered by seq_no
    linked via hash chain


Constraints

    UNIQUE (run_id, seq_no)

Guarantees

    deterministic event order.



────────────────────────────────────────────────────────────────────

                              │
                              │ optional relation
                              ▼


                    [exported_artifacts]


        exported_artifacts
        ─────────────────────────────────────────────
        artifact_id      TEXT  PK

        tenant_id        TEXT  FK → tenants
        run_id           TEXT  FK → runs  (nullable)

        artifact_type    TEXT

        file_path        TEXT
        sha256           TEXT

        created_at       TEXT


Example

        artifact_id   type         file
        -----------   ---------    -----------------
        a1            run_report   exports/run1.txt
        a2            verify_log   exports/verify1.txt


Purpose

    Track exported reports or artifacts.

Ensures:

    exported evidence remains traceable.



────────────────────────────────────────────────────────────────────

                    Entity Relationship Summary


        tenants
           │
           │ 1:N
           ▼
        runs
           │
           │ 1:N
           ▼
        audit_events

        runs
           │
           │ 1:N
           ▼
        exported_artifacts


All operational data is scoped by tenant_id.



────────────────────────────────────────────────────────────────────

                Multi-Tenant Isolation Model


All core tables include tenant_id.

Tables requiring tenant scope:

    runs
    audit_events
    exported_artifacts


Example safe query


    SELECT *
    FROM audit_events
    WHERE tenant_id = ?
      AND run_id = ?


Example unsafe query (forbidden)


    SELECT *
    FROM audit_events
    WHERE run_id = ?



────────────────────────────────────────────────────────────────────

                Append-Only Enforcement


The following tables are immutable:

    audit_events
    exported_artifacts


Database triggers block:

    UPDATE
    DELETE


Example rule

    BEFORE UPDATE → ABORT
    BEFORE DELETE → ABORT


Guarantee

    historical evidence cannot be modified.



────────────────────────────────────────────────────────────────────

                Hash Chain Relationships


Within a run:


    event_1
        prev_hash = NULL
        event_hash = H1

    event_2
        prev_hash = H1
        event_hash = H2

    event_3
        prev_hash = H2
        event_hash = H3


The last event_hash becomes:

    runs.final_chain_hash



────────────────────────────────────────────────────────────────────

                Integrity Invariants


Invariant 1

    audit_events are strictly ordered.

Invariant 2

    event chain must remain continuous.

Invariant 3

    sealed runs cannot accept new events.

Invariant 4

    tenant_id must match across all relations.



────────────────────────────────────────────────────────────────────

                Indexing Strategy


Recommended indexes


    runs

        INDEX (tenant_id)


    audit_events

        INDEX (tenant_id, run_id)
        INDEX (run_id, seq_no)


    exported_artifacts

        INDEX (tenant_id)



Purpose

    maintain tenant-scoped query performance.