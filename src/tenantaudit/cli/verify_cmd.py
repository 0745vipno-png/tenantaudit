from tenantaudit.services.verify_service import VerifyService

service = VerifyService()


def register_verify_commands(subparsers):

    verify_parser = subparsers.add_parser("verify")
    verify_sub = verify_parser.add_subparsers(dest="verify_cmd")

    run_parser = verify_sub.add_parser("run")
    run_parser.add_argument("tenant_id")
    run_parser.add_argument("run_id")
    run_parser.set_defaults(func=verify_run)


def verify_run(args):

    result = service.verify_run(args.tenant_id, args.run_id)

    print("Verification result")
    print(result)