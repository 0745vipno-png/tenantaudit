Audit Chain Model

The audit chain model defines how audit events are cryptographically linked to provide tamper-evident history.

Each audit event is connected to the previous event through a secure hash, forming a deterministic chain.

This mechanism ensures that any modification of historical data can be detected during verification.

Each tenant run maintains an independent audit chain.

Event Chain Structure

Audit events are stored in chronological order and linked together through hashes.

Event1 → Event2 → Event3 → ... → EventN

Each event contains two critical fields:

prev_hash — the hash of the previous event

event_hash — the computed hash of the current event

This creates a cryptographic linkage between all events in the run.

Event Record Model

An audit event logically contains the following fields:

Field	Description
event_id	unique event identifier
tenant_id	tenant identifier
run_id	audit run identifier
event_type	event category
payload	event data (JSON)
created_at	event timestamp
prev_hash	hash of the previous event
event_hash	hash of this event

These fields are used to compute the event hash deterministically.

Hash Computation

Each event hash is computed using a deterministic hashing process.

event_hash = SHA256(
    tenant_id +
    run_id +
    event_type +
    payload +
    created_at +
    prev_hash
)

Important requirements:

payload must use canonical JSON serialization

timestamps must use a consistent format

field ordering must remain deterministic

If these rules are violated, verification may fail.

Genesis Event

The first event in a run is called the genesis event.

Because no previous event exists, the prev_hash field must use a predefined value.

Example:

prev_hash = "GENESIS"

or

prev_hash = NULL

The specific value depends on the implementation but must remain consistent.

Chain Progression

For every new event appended to the chain:

prev_hash = last_event.event_hash
event_hash = SHA256(current_event_data + prev_hash)

This ensures that every event depends on the entire history of the chain.

If a historical event changes, all subsequent hashes become invalid.

Final Chain Hash

When a run is sealed, the final state of the chain is recorded.

final_chain_hash = last_event.event_hash

After sealing:

no new events may be appended

the chain hash becomes immutable

This allows external systems to record or store the final hash as evidence.

Chain Verification

Verification recomputes the hash chain from the stored events.

verify run <tenant_id> <run_id>

Verification procedure:

load all events for the run

recompute event hashes sequentially

verify each prev_hash reference

compare stored event_hash values

verify the final chain hash

If all checks succeed, the audit chain is considered valid.

Verification Failure Cases

Verification fails when any of the following conditions occur:

Condition	Description
hash mismatch	recomputed event hash differs from stored value
prev_hash mismatch	chain linkage is broken
missing event	an event in the chain is missing
event order corruption	events are not in chronological order
final hash mismatch	stored final chain hash does not match recomputed hash
Security Guarantees

The audit chain provides the following guarantees:

tamper-evident audit history

deterministic integrity verification

append-only event records

tenant-scoped audit isolation

Any modification to historical events will break the chain.

Limitations

TenantAudit is not a blockchain system.

The system does not provide:

distributed consensus

trustless verification

public ledger replication

external timestamp authorities

TenantAudit is designed as a local audit ledger with deterministic verification.

Implementation Reference

Relevant components in the codebase:

core/hash_engine.py
services/audit_service.py
services/verify_service.py
repositories/event_repository.py

The hash_engine module is responsible for:

event hash computation

chain progression

chain verification

The implementation must ensure deterministic hashing behavior.
