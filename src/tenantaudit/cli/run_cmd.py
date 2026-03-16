from tenantaudit.services.run_service import RunService

service = RunService()


def register_run_commands(subparsers):

    run_parser = subparsers.add_parser("run")
    run_sub = run_parser.add_subparsers(dest="run_cmd")

    # create
    create_parser = run_sub.add_parser("create")
    create_parser.add_argument("tenant_id")
    create_parser.set_defaults(func=create_run)

    # list
    list_parser = run_sub.add_parser("list")
    list_parser.add_argument("tenant_id")
    list_parser.set_defaults(func=list_runs)

    # seal
    seal_parser = run_sub.add_parser("seal")
    seal_parser.add_argument("tenant_id")
    seal_parser.add_argument("run_id")
    seal_parser.set_defaults(func=seal_run)


def create_run(args):

    run_id = service.create_run(args.tenant_id)

    print("Run created")
    print(f"run_id: {run_id}")


def list_runs(args):

    runs = service.list_runs(args.tenant_id)

    for r in runs:
        print(f"{r['run_id']} | {r['status']} | events={r['event_count']}")


def seal_run(args):

    service.seal_run(args.tenant_id, args.run_id)

    print("Run sealed")