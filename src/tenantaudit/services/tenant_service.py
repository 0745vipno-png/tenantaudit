"""
Tenant Service
==============

Business logic for tenant lifecycle.

Responsibilities
----------------
- Create tenant
- Validate tenant existence
- Ensure tenant is active
- Disable tenant
"""

from __future__ import annotations

from datetime import datetime

from tenantaudit.repositories.tenant_repository import TenantRepository


class TenantNotFoundError(Exception):
    pass


class TenantDisabledError(Exception):
    pass


class TenantAlreadyExistsError(Exception):
    pass


class TenantService:

    def __init__(self):
        self.repo = TenantRepository()


    # ---------------------------------------------------------
    # Create Tenant
    # ---------------------------------------------------------

    def create_tenant(self, tenant_name: str) -> str:

        existing = self.repo.get_tenant_by_name(tenant_name)

        if existing:
            raise TenantAlreadyExistsError(
                f"Tenant already exists: {tenant_name}"
            )

        created_at = datetime.utcnow().isoformat()

        tenant_id = self.repo.create_tenant(
            tenant_name=tenant_name,
            created_at=created_at,
        )

        return tenant_id


    # ---------------------------------------------------------
    # Get Tenant
    # ---------------------------------------------------------

    def get_tenant(self, tenant_id: str):

        tenant = self.repo.get_tenant_by_id(tenant_id)

        if tenant is None:
            raise TenantNotFoundError(tenant_id)

        return tenant


    # ---------------------------------------------------------
    # List Tenants
    # ---------------------------------------------------------

    def list_tenants(self):

        return self.repo.list_tenants()


    # ---------------------------------------------------------
    # Ensure Tenant Active
    # ---------------------------------------------------------

    def ensure_tenant_active(self, tenant_id: str):

        tenant = self.get_tenant(tenant_id)

        if tenant["status"] != "active":
            raise TenantDisabledError(
                f"Tenant disabled: {tenant_id}"
            )

        return tenant


    # ---------------------------------------------------------
    # Disable Tenant
    # ---------------------------------------------------------

    def disable_tenant(self, tenant_id: str):

        tenant = self.get_tenant(tenant_id)

        if tenant["status"] == "disabled":
            return

        self.repo.update_status(
            tenant_id=tenant_id,
            status="disabled",
        )