"""
TenantAudit CLI Entry
"""

import argparse

from tenantaudit.cli.tenant_cmd import register_tenant_commands
from tenantaudit.cli.run_cmd import register_run_commands
from tenantaudit.cli.event_cmd import register_event_commands
from tenantaudit.cli.verify_cmd import register_verify_commands


def main():

    parser = argparse.ArgumentParser(
        prog="tenantaudit",
        description="Multi-Tenant Audit Logging System"
    )

    subparsers = parser.add_subparsers(dest="command")

    # register command groups
    register_tenant_commands(subparsers)
    register_run_commands(subparsers)
    register_event_commands(subparsers)
    register_verify_commands(subparsers)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()