try:
    from .database import SessionLocal, init_db
    from .models import User, Shipment
except ImportError:
    import os, sys
    sys.path.append(os.path.dirname(__file__))
    from database import SessionLocal, init_db
    from models import User, Shipment

def run():
    init_db()
    db = SessionLocal()
    if not db.query(User).first():
        db.add_all([
            User(username="gm1",       password="demo", role="global_manager"),
            User(username="sm_sj",     password="demo", role="store_manager",   store_id="SJ01"),
            User(username="wh_sj",     password="demo", role="warehouse_staff", store_id="SJ01"),
            User(username="carrier_x", password="demo", role="carrier",         carrier_id="CAX"),
        ])
    if not db.query(Shipment).first():
        db.add_all([
            Shipment(origin_store="SJ01", destination_store="SF02", carrier_id="CAX",
                     status="created",    location="10101"),
            Shipment(origin_store="LA03", destination_store="SJ01", carrier_id="CAX",
                     status="in_transit", location="90001"),
        ])
    db.commit()
    db.close()

if __name__ == "__main__":
    run()
