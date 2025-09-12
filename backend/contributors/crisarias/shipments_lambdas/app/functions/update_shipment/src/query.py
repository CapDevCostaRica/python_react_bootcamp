from app.common.python.shared.domain.models import Shipment, Warehouse, User, ShipmentLocation, UserRole, ShipmentStatus
from app.common.python.shared.domain.schemas import ShipmentSchema
from app.common.python.shared.infrastructure.database import get_session
from app.common.python.shared.infrastructure.telemetry import logger
from app.common.python.shared.domain.models import Shipment, Warehouse
from app.common.python.shared.infrastructure.response import make_response

from sqlalchemy import func, and_

def validatesShipmentAccess(user: User, shipmentID: int, status: str) -> tuple[bool, dict]:
    session = None
    try:
        session = get_session()
        shipment = session.query(Shipment).filter(Shipment.id == shipmentID).first()
        if not shipment:
            logger.error(f"Shipment not found: {shipmentID}")
            return (False, make_response({"error": "Shipment not found"}, 404))
        isWarehouseStaff = user.get("role") == UserRole.warehouse_staff
        isCarrier = user.get("role") == UserRole.carrier
        user_warehouse_id = user.get("warehouse_id", "")        
        if isWarehouseStaff:            
            if  status == ShipmentStatus.in_transit and shipment.origin_warehouse_id != user_warehouse_id:
                unauthorizedMessage = f"Just warehouse staff from the origin warehouse can mark shipment {shipmentID} as in_transit"
                logger.error(unauthorizedMessage)
                return (False, make_response({"error": unauthorizedMessage}, 403))
            if  status == ShipmentStatus.delivered and shipment.destination_warehouse_id != user_warehouse_id:
                unauthorizedMessage = f"Just warehouse staff from the destination warehouse can mark shipment {shipmentID} as delivered"
                logger.error(unauthorizedMessage)
                return (False, make_response({"error": unauthorizedMessage}, 403))
        if isCarrier and shipment.assigned_carrier_id != user.get("id"):
            unauthorizedMessage = f"User {user.get('username')} is not authorized to update shipment {shipmentID}"
            logger.error(unauthorizedMessage)
            return (False, make_response({"error": unauthorizedMessage}, 403))
        # Validate shipment location before allowing status update
        if isWarehouseStaff and status == ShipmentStatus.delivered:
            currentLocation = session.query(ShipmentLocation).filter(ShipmentLocation.shipment_id == shipmentID).order_by(ShipmentLocation.id.desc()).first()
            validLocation = session.query(Warehouse).filter(
                and_(
                    Warehouse.id == shipment.destination_warehouse_id,
                    Warehouse.postal_code == currentLocation.postal_code
                ) 
            ).first()
            locationErrorMessage = f"The shipment {shipmentID} cannot be marked as {status.value} from the current location {currentLocation.postal_code if currentLocation else 'unknown'}"
            if not validLocation:
                logger.error(locationErrorMessage)
                return (False, make_response({"error": locationErrorMessage}, 400))
        return (True, { "shipment": shipment })
    except Exception as e:
        logger.error(f"Error validating shipment: {e}")
        return (False, make_response({"error": "Internal Server Error"}, 500))
    finally:
        session.close()

def UpdateShipment(user: User, shipment: Shipment, status: str, location: str) -> tuple[bool, dict]:
    isWarehouseStaff = user.get("role") == UserRole.warehouse_staff
    isCarrier = user.get("role") == UserRole.carrier
    if isWarehouseStaff:
        return UpdateShipmentStatus(shipment, status, user.get("id"))
    if isCarrier:
        return updateShipmentLocation(shipment, location)

def UpdateShipmentStatus(shipment: Shipment, status: str, userID: int) -> tuple[bool, dict]:
    session = None
    try:
        session = get_session()
        if status == ShipmentStatus.in_transit and shipment.status != ShipmentStatus.created:
            errorMessage = f"Shipment {shipment.id} must be in 'created' status to be marked as 'in_transit'"
            logger.error(errorMessage)
            return (False, make_response({"error": errorMessage}, 400))
        if status == ShipmentStatus.delivered and shipment.status != ShipmentStatus.in_transit:
            errorMessage = f"Shipment {shipment.id} must be in 'in_transit' status to be marked as 'delivered'"
            logger.error(errorMessage)
            return (False, make_response({"error": errorMessage}, 400))
        if status == ShipmentStatus.created:
            errorMessage = f"Shipment {shipment.id} cannot be reverted to 'created' status"
            logger.error(errorMessage)
            return (False, make_response({"error": errorMessage}, 400))
        shipment.status = status
        if status == ShipmentStatus.in_transit:            
            shipment.in_transit_at = func.now()
            shipment.in_transit_by_id = userID
        if status == ShipmentStatus.delivered:            
            shipment.delivered_at = func.now()
            shipment.delivered_by_id = userID
        session.commit()
        logger.info(f"Shipment {shipment.id} status updated to {status.value} by user {userID}")
        return (True, make_response({"message": "Shipment status updated successfully"}, 200))
    except Exception as e:
        logger.error(f"Error updating shipment location: {e}")
        return (False, make_response({"error": "Internal Server Error"}, 500))
    finally:
        session.close()

def updateShipmentLocation(shipment: Shipment, location: str) -> tuple[bool, dict]:
    session = None
    try:
        if shipment.status != ShipmentStatus.in_transit:
            errorMessage = f"Shipment {shipment.id} must be in 'in_transit' to update its location"
            logger.error(errorMessage)
            return (False, make_response({"error": errorMessage}, 400))
        session = get_session()
        newRow = ShipmentLocation(shipment_id=shipment.id, postal_code=location)
        session.add(newRow)
        logger.info(f"Added new location for shipment {shipment.id}: {location}")
        session.commit()
        return (True, make_response({"message": "Shipment location updated successfully"}, 200))
    except Exception as e:
        logger.error(f"Error updating shipment location: {e}")
        return (False, make_response({"error": "Internal Server Error"}, 500))
    finally:
        session.close()