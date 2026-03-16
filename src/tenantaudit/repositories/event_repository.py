"""
Event Repository
================

Responsible for persistence of audit events.

Responsibilities
----------------
- Fetch last event in a run
- Insert new audit event
- Fetch events for verification
- Maintain append-only model

This layer does NOT enforce business rules
such as run state validation.
"""

from __future__ import annotations

from typing import Optional, List
import uuid

from tenantaudit.storage.db import get_connection
from tenantaudit.core.hash_engine import compute_event_hash


class EventRepository:

    # ---------------------------------------------------------
    # Last Event
    # ---------------------------------------------------------

    def get_last_event(self, tenant_id: str, run_id: str):

        conn = get_connection()

        cursor = conn.execute(
            """
            SELECT *
            FROM audit_events
            WHERE tenant_id = ?
              AND run_id = ?
            ORDER BY seq_no DESC
            LIMIT 1
            """,
            (tenant_id, run_id),
        )

        row = cursor.fetchone()
        conn.close()

        return row


    # ---------------------------------------------------------
    # Insert Event
    # ---------------------------------------------------------

    def insert_event(
        self,
        tenant_id: str,
        run_id: str,
        event_type: str,
        payload: dict,
        occurred_at: str,
    ) -> str:
        """
        Append a new audit event.

        Returns
        -------
        event_id
        """

        conn = get_connection()

        try:

            # -----------------------------------
            # determine sequence number
            # -----------------------------------

            cursor = conn.execute(
                """
                SELECT seq_no, event_hash
                FROM audit_events
                WHERE tenant_id = ?
                  AND run_id = ?
                ORDER BY seq_no DESC
                LIMIT 1
                """,
                (tenant_id, run_id),
            )

            row = cursor.fetchone()

            if row is None:
                seq_no = 1
                prev_hash = None
            else:
                seq_no = row["seq_no"] + 1
                prev_hash = row["event_hash"]


            # -----------------------------------
            # compute hash
            # -----------------------------------

            event_hash = compute_event_hash(
                tenant_id=tenant_id,
                run_id=run_id,
                seq_no=seq_no,
                event_type=event_type,
                payload=payload,
                occurred_at=occurred_at,
                prev_hash=prev_hash,
            )


            # -----------------------------------
            # create event id
            # -----------------------------------

            event_id = str(uuid.uuid4())


            # -----------------------------------
            # payload canonical JSON
            # -----------------------------------

            import json

            payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))


            # -----------------------------------
            # insert event
            # -----------------------------------

            conn.execute(
                """
                INSERT INTO audit_events (
                    event_id,
                    tenant_id,
                    run_id,
                    seq_no,
                    event_type,
                    payload_json,
                    occurred_at,
                    prev_hash,
                    event_hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    tenant_id,
                    run_id,
                    seq_no,
                    event_type,
                    payload_json,
                    occurred_at,
                    prev_hash,
                    event_hash,
                ),
            )

            conn.commit()

            return event_id

        finally:
            conn.close()


    # ---------------------------------------------------------
    # Fetch Events
    # ---------------------------------------------------------

    def get_events_by_run(
        self,
        tenant_id: str,
        run_id: str,
    ) -> List:

        conn = get_connection()

        cursor = conn.execute(
            """
            SELECT *
            FROM audit_events
            WHERE tenant_id = ?
              AND run_id = ?
            ORDER BY seq_no ASC
            """,
            (tenant_id, run_id),
        )

        rows = cursor.fetchall()
        conn.close()

        return rows


    # ---------------------------------------------------------
    # Count Events
    # ---------------------------------------------------------

    def count_events(self, tenant_id: str, run_id: str) -> int:

        conn = get_connection()

        cursor = conn.execute(
            """
            SELECT COUNT(*) as count
            FROM audit_events
            WHERE tenant_id = ?
              AND run_id = ?
            """,
            (tenant_id, run_id),
        )

        row = cursor.fetchone()
        conn.close()

        return row["count"]