from backend.contributors.majocr.shipments_lambdas.app.common.python.common.authentication.require_role_decorator import require_role


@require_role("store_manager", "warehouse_staff")
def handler(event, context):
    pass