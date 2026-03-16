"""
TenantAudit Hash Engine
=======================

Provides deterministic hashing for audit events.

Responsibilities
----------------
- Canonical event serialization
- SHA256 hashing
- Payload normalization
- Hash chain linkage

Security Model
--------------
The event hash includes tenant_id to prevent cross-tenant chain injection.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


# ---------------------------------------------------------
# Canonical JSON
# ---------------------------------------------------------

def canonicalize_payload(payload: Dict[str, Any]) -> str:
    """
    Serialize payload JSON deterministically.

    Ensures:
    - sorted keys
    - stable formatting
    """

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


# ---------------------------------------------------------
# Event Serialization
# ---------------------------------------------------------

def serialize_event(
    tenant_id: str,
    run_id: str,
    seq_no: int,
    event_type: str,
    payload_json: str,
    occurred_at: str,
    prev_hash: str | None,
) -> str:
    """
    Produce canonical event string.

    Format

        tenant_id|run_id|seq_no|event_type|payload|timestamp|prev_hash
    """

    prev_hash_value = prev_hash if prev_hash is not None else "NULL"

    parts = [
        tenant_id,
        run_id,
        str(seq_no),
        event_type,
        payload_json,
        occurred_at,
        prev_hash_value,
    ]

    return "|".join(parts)


# ---------------------------------------------------------
# SHA256
# ---------------------------------------------------------

def sha256_hash(data: str) -> str:
    """
    Compute SHA256 hex digest.
    """

    return hashlib.sha256(data.encode("utf-8")).hexdigest()


# ---------------------------------------------------------
# Event Hash
# ---------------------------------------------------------

def compute_event_hash(
    tenant_id: str,
    run_id: str,
    seq_no: int,
    event_type: str,
    payload: Dict[str, Any],
    occurred_at: str,
    prev_hash: str | None,
) -> str:
    """
    Compute the event hash for an audit event.
    """

    payload_json = canonicalize_payload(payload)

    canonical_string = serialize_event(
        tenant_id=tenant_id,
        run_id=run_id,
        seq_no=seq_no,
        event_type=event_type,
        payload_json=payload_json,
        occurred_at=occurred_at,
        prev_hash=prev_hash,
    )

    return sha256_hash(canonical_string)


# ---------------------------------------------------------
# Chain Verification Helper
# ---------------------------------------------------------

def recompute_event_hash(event_row) -> str:
    """
    Recompute hash from database row.

    event_row should provide:

        tenant_id
        run_id
        seq_no
        event_type
        payload_json
        occurred_at
        prev_hash
    """

    canonical_string = serialize_event(
        tenant_id=event_row["tenant_id"],
        run_id=event_row["run_id"],
        seq_no=event_row["seq_no"],
        event_type=event_row["event_type"],
        payload_json=event_row["payload_json"],
        occurred_at=event_row["occurred_at"],
        prev_hash=event_row["prev_hash"],
    )

    return sha256_hash(canonical_string)