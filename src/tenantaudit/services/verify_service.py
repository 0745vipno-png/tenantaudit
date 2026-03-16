"""
Verify Service
==============

Provides audit chain verification.

Responsibilities
----------------
- Recompute event hashes
- Validate prev_hash linkage
- Compare final_chain_hash
- Detect tampering
"""

from __future__ import annotations

from typing import Dict, Any

from tenantaudit.repositories.event_repository import EventRepository
from tenantaudit.services.tenant_service import TenantService
from tenantaudit.services.run_service import RunService
from tenantaudit.core.hash_engine import recompute_event_hash


class VerificationError(Exception):
    pass


class VerifyService:

    def __init__(self):
        self.event_repo = EventRepository()
        self.tenant_service = TenantService()
        self.run_service = RunService()

    # ---------------------------------------------------------
    # Verify Run
    # ---------------------------------------------------------

    def verify_run(self, tenant_id: str, run_id: str) -> Dict[str, Any]:
        """
        Verify integrity of an audit run.
        """

        # ensure tenant active
        self.tenant_service.ensure_tenant_active(tenant_id)

        # load run
        run = self.run_service.get_run(tenant_id, run_id)

        # load events
        events = self.event_repo.get_events_by_run(tenant_id, run_id)

        expected_prev = None
        last_hash = None

        for event in events:

            # verify prev_hash linkage
            if event["prev_hash"] != expected_prev:
                raise VerificationError(
                    f"Chain break at seq {event['seq_no']}"
                )

            # recompute hash
            recomputed_hash = recompute_event_hash(event)

            if recomputed_hash != event["event_hash"]:
                raise VerificationError(
                    f"Hash mismatch at seq {event['seq_no']}"
                )

            expected_prev = event["event_hash"]
            last_hash = event["event_hash"]

        # check event_count
        if len(events) != run["event_count"]:
            raise VerificationError(
                "Event count mismatch"
            )

        # check final chain hash
        if run["final_chain_hash"] != last_hash:
            raise VerificationError(
                "Final chain hash mismatch"
            )

        return {
            "status": "valid",
            "run_id": run_id,
            "event_count": len(events),
            "final_hash": last_hash,
        }