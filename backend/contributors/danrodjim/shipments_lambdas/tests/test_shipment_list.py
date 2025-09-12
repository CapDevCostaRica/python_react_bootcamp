import pytest
import json
from http import HTTPStatus
from app.functions.shipment.shipment_create.src.app import handler

@pytest.fixture
def base_event():
    return {
        "body": json.dumps({}),
        "claims": {"role": "global_manager", "id": 1, "warehouse_id": 10},
        "isBase64Enconded": False,
    }

# 1. Successful shipment list without status filter
def test_successful_listing_no_status_filter(base_event):
    result = handler(base_event, None)
    assert result["statusCode"] == HTTPStatus.OK

# 2. Successful shipment list with status filter
def test_successful_listing_with_status_filter(base_event):
    base_event["body"] = json.dumps({"status": "created"})
    result = handler(base_event, None)
    assert result["statusCode"] == HTTPStatus.OK

# 3. Successful shipment list with date filter
def test_successful_listing_with_date_filter(base_event):
    base_event["body"] = json.dumps({"date": "2025-01-01"})
    result = handler(base_event, None)
    assert result["statusCode"] == HTTPStatus.OK

# 4. Successful shipment list with carrier filter
def test_successful_listing_with_carrier_filter(base_event):
    base_event["body"] = json.dumps({"carrier": 1})
    result = handler(base_event, None)
    assert result["statusCode"] == HTTPStatus.OK

# 5. Successful shipment list with id filter
def test_successful_listing_with_id_filter(base_event):
    base_event["body"] = json.dumps({"id": 1})
    result = handler(base_event, None)
    assert result["statusCode"] == HTTPStatus.OK

# 6. Successful shipment list with multiple filters (all of them)
def test_successful_listing_with_multiple_filters(base_event):
    base_event["body"] = json.dumps({
        "id": 1,
        "status": "created",
        "date": "2025-01-01",
        "carrier": 1,
    })
    result = handler(base_event, None)
    assert result["statusCode"] == HTTPStatus.OK

# 7. Successful shipment list with role of global_manager
def test_global_manager_view_all(base_event):
    base_event["claims"]["role"] = "global_manager"
    result = handler(base_event, None)
    assert result["statusCode"] == HTTPStatus.OK

# 8. Successful shipment list with role of store_manager
def test_store_manager_limited_view(base_event):
    base_event["claims"]["role"] = "store_manager"
    base_event["claims"]["warehouse_id"] = 10
    result = handler(base_event, None)
    assert result["statusCode"] == HTTPStatus.OK

# 9. Successful shipment list with role of warehouse_staff
def test_warehouse_staff_limited_view(base_event):
    base_event["claims"]["role"] = "warehouse_staff"
    base_event["claims"]["warehouse_id"] = 10
    result = handler(base_event, None)
    assert result["statusCode"] == HTTPStatus.OK

# 10. Successful shipment list with role of carrier
def test_carrier_assigned_shipments_view(base_event):
    base_event["claims"]["role"] = "carrier"
    base_event["claims"]["id"] = 1
    result = handler(base_event, None)
    assert result["statusCode"] == HTTPStatus.OK

## These last 3 tests are testing required_role decorator, but I placed them here because they are in the list 
## of use cases for the shipment listing endpoint

# 11. Failed shipment list because of invalid token
def test_failed_listing_invalid_token(base_event):
    base_event["claims"] = None
    result = handler(base_event, None)
    assert result["statusCode"] in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)

# 12. Failed shipment list because of missing token
def test_failed_listing_missing_token(base_event):
    base_event.pop("claims", None)
    result = handler(base_event, None)
    assert result["statusCode"] in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)

# 13. Failed shipment list because of unauthorized role
def test_failed_listing_unauthorized_role(base_event):
    base_event["claims"]["role"] = "unauthorized_role"
    result = handler(base_event, None)
    assert result["statusCode"] in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
