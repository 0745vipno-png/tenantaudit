"""
Run Service
===========

Business logic for audit run lifecycle.

Responsibilities
----------------
- Create runs
- Validate run state
- Seal runs
- Retrieve runs
"""

from __future__ import annotations

from datetime import datetime

from tenantaudit.repositories.run_repository import RunRepository
from tenantaudit.services.tenant_service import TenantService


class RunNotFoundError(Exception):
    pass


class RunClosedError(Exception):
    pass


class RunService:

    def __init__(self):
        self.repo = RunRepository()
        self.tenant_service = TenantService()


    # ---------------------------------------------------------
    # Create Run
    # ---------------------------------------------------------

    def create_run(self, tenant_id: str) -> str:

        # ensure tenant active
        self.tenant_service.ensure_tenant_active(tenant_id)

        started_at = datetime.utcnow().isoformat()

        run_id = self.repo.create_run(
            tenant_id=tenant_id,
            started_at=started_at,
        )

        return run_id


    # ---------------------------------------------------------
    # Get Run
    # ---------------------------------------------------------

    def get_run(self, tenant_id: str, run_id: str):

        run = self.repo.get_run(
            tenant_id=tenant_id,
            run_id=run_id,
        )

        if run is None:
            raise RunNotFoundError(run_id)

        return run


    # ---------------------------------------------------------
    # List Runs
    # ---------------------------------------------------------

    def list_runs(self, tenant_id: str):

        self.tenant_service.ensure_tenant_active(tenant_id)

        return self.repo.list_runs_by_tenant(tenant_id)


    # ---------------------------------------------------------
    # Ensure Run Open
    # ---------------------------------------------------------

    def ensure_run_open(self, tenant_id: str, run_id: str):

        run = self.get_run(tenant_id, run_id)

        if run["status"] != "open":
            raise RunClosedError(
                f"Run already sealed: {run_id}"
            )

        return run


    # ---------------------------------------------------------
    # Seal Run
    # ---------------------------------------------------------

    def seal_run(self, tenant_id: str, run_id: str):

        # ensure tenant active
        self.tenant_service.ensure_tenant_active(tenant_id)

        # ensure run open
        self.ensure_run_open(tenant_id, run_id)

        sealed_at = datetime.utcnow().isoformat()

        self.repo.seal_run(
            tenant_id=tenant_id,
            run_id=run_id,
            sealed_at=sealed_at,
        )