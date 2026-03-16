# TenantAudit

TenantAudit is a multi-tenant, append-only audit logging system designed for tamper-evident evidence recording and verification.

It provides a deterministic audit trail where every event is linked through a cryptographic hash chain.  
Each tenant maintains its own isolated audit history.

The system is implemented as a CLI-first tool intended for operational environments where traceability and verification are required.

---

## Key Features

### Multi-Tenant Isolation

Each tenant maintains a logically isolated audit history.

All operations are scoped by:


tenant_id


Cross-tenant access is prevented by design.

---

### Append-Only Audit Storage

Audit events are immutable.

The database enforces:


UPDATE → forbidden
DELETE → forbidden


via SQLite triggers.

---

### Tamper-Evident Hash Chain

Each audit event contains:


prev_hash
event_hash


forming a cryptographic chain.


Event1 → Event2 → Event3 → ...


If any historical event is modified, verification will fail.

---

### Run-Based Audit Sessions

Audit events are grouped into **Runs**.

Lifecycle:


create_run → open → seal_run → sealed


Once sealed:


no further events allowed


---

### Deterministic Verification

The system can recompute the entire event chain:


verify run <tenant_id> <run_id>


Verification checks:

- event hash integrity
- prev_hash linkage
- final_chain_hash
- event_count

---

## Architecture Overview

This architecture separates command handling, business rules,
data persistence, and hash-chain verification into distinct layers.

The layered design keeps CLI interaction, business logic,
data access, and integrity verification clearly separated.

The design emphasizes:

- tenant isolation
- append-only evidence storage
- deterministic chain verification
- predictable CLI-first operation

---

## Architecture Diagram

```text
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

Project Structure
core/
    hash_engine.py

storage/
    db.py

repositories/
    tenant_repository.py
    run_repository.py
    event_repository.py

services/
    tenant_service.py
    run_service.py
    audit_service.py
    verify_service.py

cli/
    main.py
    
---

## Installation

Clone the repository:


git clone <repo_url>
cd tenantaudit


Set Python path (PowerShell):


$env:PYTHONPATH = ".\src"


---

## Usage

### Create Tenant


python -m tenantaudit.cli.main tenant create "Acme"


### List Tenants


python -m tenantaudit.cli.main tenant list


### Create Run


python -m tenantaudit.cli.main run create <tenant_id>


### Append Event


python -m tenantaudit.cli.main event append <tenant_id> <run_id> <event_type> <json_payload>


Example (PowerShell):


python -m tenantaudit.cli.main event append <T_ID> <R_ID> LOGIN "{""user"":""admin""}"


### Seal Run


python -m tenantaudit.cli.main run seal <tenant_id> <run_id>


### Verify Run


python -m tenantaudit.cli.main verify run <tenant_id> <run_id>


Example output:


{
"status": "valid",
"run_id": "...",
"event_count": 3,
"final_hash": "..."
}


---

## Security Model

The system guarantees:

- append-only evidence storage
- tamper-evident event chains
- tenant-scoped audit histories
- deterministic verification

The system **does not provide**:

- distributed consensus
- blockchain trustless verification
- external timestamp authorities

TenantAudit is an **audit ledger**, not a blockchain.

---

## License

This project is licensed under the **GNU General Public License v3.0**.

See the `LICENSE` file for details.