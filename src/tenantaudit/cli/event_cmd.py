import json

from tenantaudit.services.audit_service import AuditService

service = AuditService()


def register_event_commands(subparsers):

    event_parser = subparsers.add_parser("event")
    event_sub = event_parser.add_subparsers(dest="event_cmd")

    append_parser = event_sub.add_parser("append")
    append_parser.add_argument("tenant_id")
    append_parser.add_argument("run_id")
    append_parser.add_argument("event_type")
    append_parser.add_argument("payload")

    append_parser.set_defaults(func=append_event)


def append_event(args):

    payload = json.loads(args.payload)

    event_id = service.append_event(
        tenant_id=args.tenant_id,
        run_id=args.run_id,
        event_type=args.event_type,
        payload=payload
    )

    print("Event appended")
    print(f"event_id: {event_id}")