from app.common.python.common.authentication.require_role import require_role

@require_role( "global_manager", "store_manager", "warehouse_staff", "carrier")
def handler(event, context):
    # TODO: implement the handler logic
    pass