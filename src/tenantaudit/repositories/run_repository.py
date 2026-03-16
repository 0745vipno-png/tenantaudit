"""
Run Repository
==============

Responsible for persistence of audit runs.

Responsibilities
----------------
- Create audit runs
- Retrieve runs
- Seal runs
- List runs for tenant

Does NOT enforce run state validation.
"""

from __future__ import annotations

import uuid

from tenantaudit.storage.db import get_connection
from tenantaudit.repositories.event_repository import EventRepository


class RunRepository:

    def __init__(self):
        self.event_repo = EventRepository()


    # ---------------------------------------------------------
    # Create Run
    # ---------------------------------------------------------

    def create_run(self, tenant_id: str, started_at: str) -> str:

        run_id = str(uuid.uuid4())

        conn = get_connection()

        conn.execute(
            """
            INSERT INTO runs (
                run_id,
                tenant_id,
                status,
                started_at,
                event_count
            )
            VALUES (?, ?, 'open', ?, 0)
            """,
            (
                run_id,
                tenant_id,
                started_at,
            ),
        )

        conn.commit()
        conn.close()

        return run_id


    # ---------------------------------------------------------
    # Get Run
    # ---------------------------------------------------------

    def get_run(self, tenant_id: str, run_id: str):

        conn = get_connection()

        cursor = conn.execute(
            """
            SELECT *
            FROM runs
            WHERE tenant_id = ?
              AND run_id = ?
            """,
            (
                tenant_id,
                run_id,
            ),
        )

        row = cursor.fetchone()
        conn.close()

        return row


    # ---------------------------------------------------------
    # List Runs
    # ---------------------------------------------------------

    def list_runs_by_tenant(self, tenant_id: str):

        conn = get_connection()

        cursor = conn.execute(
            """
            SELECT *
            FROM runs
            WHERE tenant_id = ?
            ORDER BY started_at DESC
            """,
            (tenant_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        return rows


    # ---------------------------------------------------------
    # Seal Run
    # ---------------------------------------------------------

    def seal_run(self, tenant_id: str, run_id: str, sealed_at: str):

        conn = get_connection()

        try:

            # -----------------------------------
            # get last event
            # -----------------------------------

            last_event = self.event_repo.get_last_event(
                tenant_id=tenant_id,
                run_id=run_id,
            )

            if last_event is None:
                final_chain_hash = None
            else:
                final_chain_hash = last_event["event_hash"]


            # -----------------------------------
            # count events
            # -----------------------------------

            event_count = self.event_repo.count_events(
                tenant_id=tenant_id,
                run_id=run_id,
            )


            # -----------------------------------
            # update run
            # -----------------------------------

            conn.execute(
                """
                UPDATE runs
                SET
                    status = 'sealed',
                    sealed_at = ?,
                    final_chain_hash = ?,
                    event_count = ?
                WHERE
                    tenant_id = ?
                    AND run_id = ?
                """,
                (
                    sealed_at,
                    final_chain_hash,
                    event_count,
                    tenant_id,
                    run_id,
                ),
            )

            conn.commit()

        finally:
            conn.close()