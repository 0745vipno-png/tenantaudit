from tenantaudit.services.tenant_service import TenantService


service = TenantService()


def register_tenant_commands(subparsers):

    tenant_parser = subparsers.add_parser("tenant")
    tenant_sub = tenant_parser.add_subparsers(dest="tenant_cmd")

    # create
    create_parser = tenant_sub.add_parser("create")
    create_parser.add_argument("name")
    create_parser.set_defaults(func=create_tenant)

    # list
    list_parser = tenant_sub.add_parser("list")
    list_parser.set_defaults(func=list_tenants)


def create_tenant(args):

    tenant_id = service.create_tenant(args.name)

    print("Tenant created")
    print(f"id: {tenant_id}")


def list_tenants(args):

    tenants = service.list_tenants()

    for t in tenants:
        print(f"{t['tenant_id']} | {t['tenant_name']} | {t['status']}")