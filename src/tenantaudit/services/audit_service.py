"""
Audit Service
=============

Business logic for appending audit events.

Responsibilities
----------------
- Validate tenant state
- Validate run state
- Append audit event
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from tenantaudit.repositories.event_repository import EventRepository
from tenantaudit.services.tenant_service import TenantService
from tenantaudit.services.run_service import RunService


class AuditService:

    def __init__(self):
        self.event_repo = EventRepository()
        self.tenant_service = TenantService()
        self.run_service = RunService()


    # ---------------------------------------------------------
    # Append Event
    # ---------------------------------------------------------

    def append_event(
        self,
        tenant_id: str,
        run_id: str,
        event_type: str,
        payload: Dict[str, Any],
    ) -> str:
        """
        Append an audit event to a run.
        """

        # ensure tenant active
        self.tenant_service.ensure_tenant_active(tenant_id)

        # ensure run open
        self.run_service.ensure_run_open(tenant_id, run_id)

        occurred_at = datetime.utcnow().isoformat()

        event_id = self.event_repo.insert_event(
            tenant_id=tenant_id,
            run_id=run_id,
            event_type=event_type,
            payload=payload,
            occurred_at=occurred_at,
        )

        return event_id