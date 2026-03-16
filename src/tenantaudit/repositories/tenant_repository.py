"""
Tenant Repository
=================

Responsible for persistence of tenant records.

Responsibilities
----------------
- Create tenant
- Fetch tenant
- List tenants
- Update tenant status

This layer does NOT enforce business rules
such as tenant state validation.
"""

from __future__ import annotations

import uuid

from tenantaudit.storage.db import get_connection


class TenantRepository:


    # ---------------------------------------------------------
    # Create Tenant
    # ---------------------------------------------------------

    def create_tenant(self, tenant_name: str, created_at: str) -> str:

        tenant_id = str(uuid.uuid4())

        conn = get_connection()

        conn.execute(
            """
            INSERT INTO tenants (
                tenant_id,
                tenant_name,
                status,
                created_at
            )
            VALUES (?, ?, 'active', ?)
            """,
            (
                tenant_id,
                tenant_name,
                created_at,
            ),
        )

        conn.commit()
        conn.close()

        return tenant_id


    # ---------------------------------------------------------
    # Get Tenant by ID
    # ---------------------------------------------------------

    def get_tenant_by_id(self, tenant_id: str):

        conn = get_connection()

        cursor = conn.execute(
            """
            SELECT *
            FROM tenants
            WHERE tenant_id = ?
            """,
            (tenant_id,),
        )

        row = cursor.fetchone()
        conn.close()

        return row


    # ---------------------------------------------------------
    # Get Tenant by Name
    # ---------------------------------------------------------

    def get_tenant_by_name(self, tenant_name: str):

        conn = get_connection()

        cursor = conn.execute(
            """
            SELECT *
            FROM tenants
            WHERE tenant_name = ?
            """,
            (tenant_name,),
        )

        row = cursor.fetchone()
        conn.close()

        return row


    # ---------------------------------------------------------
    # List Tenants
    # ---------------------------------------------------------

    def list_tenants(self):

        conn = get_connection()

        cursor = conn.execute(
            """
            SELECT *
            FROM tenants
            ORDER BY created_at ASC
            """
        )

        rows = cursor.fetchall()
        conn.close()

        return rows


    # ---------------------------------------------------------
    # Update Status
    # ---------------------------------------------------------

    def update_status(self, tenant_id: str, status: str):

        conn = get_connection()

        conn.execute(
            """
            UPDATE tenants
            SET status = ?
            WHERE tenant_id = ?
            """,
            (
                status,
                tenant_id,
            ),
        )

        conn.commit()
        conn.close()