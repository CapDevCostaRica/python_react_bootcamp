from app.common.python.common.authentication.require_role import require_role

@require_role("global_manger", "store_manager", "warehouse_staff", "carrier")
def handler(event, context):
    return {
        "statusCode": 200,
        "body": "Hello, World!"
    }