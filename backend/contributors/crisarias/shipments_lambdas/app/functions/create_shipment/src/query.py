from app.common.python.shared.domain.models import Shipment, Warehouse, User, ShipmentLocation, UserRole, ShipmentStatus
from app.common.python.shared.domain.schemas import ShipmentSchema
from app.common.python.shared.infrastructure.database import get_session
from app.common.python.shared.infrastructure.telemetry import logger
from app.common.python.shared.domain.models import Shipment, Warehouse
from app.common.python.shared.infrastructure.response import make_response

from sqlalchemy import or_


def createShipment(user: User, originWarehouseID: int, destinationWarehouseID: int, carrierID: int) -> tuple[bool, dict]:
    session = None
    try:
        logger.info(f"Creating shipment from {originWarehouseID} to {destinationWarehouseID} with carrier {carrierID} by user {user.get('username')}")
        session = get_session()
        if originWarehouseID == destinationWarehouseID:
            errorMessage = "Origin and destination warehouse cannot be the same"
            logger.error(errorMessage)
            return (False, make_response({"error": errorMessage}, 400))
        # Validate origin warehouse and destination warehouse
        warehouses = session.query(Warehouse).filter(or_(
            Warehouse.id == originWarehouseID,
            Warehouse.id == destinationWarehouseID
        )).all()
        originWareHouse = next((w for w in warehouses if w.id == originWarehouseID), None)
        destinationWareHouse = next((w for w in warehouses if w.id == destinationWarehouseID), None)
        if originWareHouse is None or destinationWareHouse is None:
            errorMessage = "Origin warehouse not found" if originWareHouse is None else "Destination warehouse not found"
            logger.error(errorMessage)
            return (False, make_response({"error": errorMessage}, 400))
        carrier = session.query(User).filter(User.id == carrierID and User.role == UserRole.carrier).first()
        if not carrier:
            errorMessage = "Invalid carrier: not found or user is not a carrier"
            logger.error(errorMessage)
            return (False, make_response({"error": errorMessage}, 400))
        newShipment = Shipment(
            origin_warehouse_id=originWarehouseID,
            destination_warehouse_id=destinationWarehouseID,
            assigned_carrier_id=carrierID,
            created_by_id=user.get("id"),
            status=ShipmentStatus.created
        )        
        session.add(newShipment)
        session.flush()  # Flush to get the ID without committing
        
        initialLocation = ShipmentLocation(
            shipment_id=newShipment.id,
            postal_code=originWareHouse.postal_code
        )
        session.add(initialLocation)
        session.commit()  # Single commit for the entire transaction
        shipmentData = ShipmentSchema().dump({
            "id": newShipment.id,
            "status": newShipment.status,
            "created_at": newShipment.created_at,
            "origin_warehouse": {
                "name": originWareHouse.name,
                "postal_code": originWareHouse.postal_code,
            },
            "target_warehouse": {
                "name": destinationWareHouse.name,
                "postal_code": destinationWareHouse.postal_code,
            },
            "carrier": {"username": carrier.username},
            "created_by": {"username": user.get("username")},
            "shipment_locations": []
        })
        return (True, make_response(
            {"message": "Shipment created successfully", "result": shipmentData},
            201))
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating shipment: {e}")
        return (False, make_response({"error": "Internal Server Error"}, 500))
    finally:
        if session:
            session.close()