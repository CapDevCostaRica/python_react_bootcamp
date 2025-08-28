import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../framework')))
from database import get_session
from services.telemetry import setupLogger

logger = setupLogger()

def closeSession(session):
    if session:
        session.close()

def insertCachedResources(model, resources):
    session = None
    try:
        session = get_session()
        # Get all existing ids in one query for efficiency
        resource_ids = [resource["index"] for resource in resources]
        existing_ids = set(r[0] for r in session.query(model.index).filter(model.index.in_(resource_ids)).all())
        new_resources = [resource for resource in resources if resource["index"] not in existing_ids]
        for resource in new_resources:
            session.add(model(**resource))
        session.commit()
        logger.info(f"Inserted {len(new_resources)} cached resources for model {model.__name__}")
    except Exception as e:
        logger.error(f"Error inserting cached resources for model {model.__name__}: {e}")
    finally:
        closeSession(session)



def getCachedResources(model):
    session = None
    try:
        session = get_session()
        resources = session.query(model.index, model.name, model.url).all()
        logger.info(f"Retrieved {len(resources)} cached resources for model {model.__name__}")
        # Return list of dicts with index, name, url
        return [{"index": r[0], "name": r[1], "url": r[2]} for r in resources]
    except Exception as e:
        logger.error(f"Error retrieving cached resources for model {model.__name__}: {e}")
    finally:
        closeSession(session)

def upsertCachedResource(model, index, body):
    session = None
    try:
        session = get_session()
        resource = session.query(model).filter(model.index == index).first()                
        if resource is not None:
            # Update the body with the provided body dict                        
            resource.body = body
            logger.info(f"Updated cached resource for model {model.__name__} with index {index}")
        else:
            newRow = model(index=body["index"], name=body["name"], url=body["url"], body=body)
            session.add(newRow)
            logger.info(f"Inserted cached resource for model {model.__name__} with index {index}")
        session.commit()
    except Exception as e:
        logger.error(f"Error inserting cached resource for model {model.__name__} with index {index}: {e}")
    finally:
        closeSession(session)

def getCachedResourceByIndex(model, index):
    session = None
    try:
        session = get_session()
        resource = session.query(model.body).filter(model.index == index).first()
        if resource is not None and resource[0]:
            logger.info(f"Retrieved cached resource for model {model.__name__} with index {index}")
            return resource[0]
        else:
            logger.warning(f"Cache miss for model {model.__name__} with index {index}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving cached resource for model {model.__name__} with index {index}: {e}")
        return None
    finally:
        closeSession(session)