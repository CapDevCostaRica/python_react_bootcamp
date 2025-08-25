import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../framework')))
from database import get_session
from services.telemetry import setupLogger

logger = setupLogger()

def insertCachedResources(model, resources):
    try:
        session = get_session()
        # Get all existing ids in one query for efficiency
        resource_ids = [resource["id"] for resource in resources]
        existing_ids = set(r[0] for r in session.query(model.id).filter(model.id.in_(resource_ids)).all())
        new_resources = [resource for resource in resources if resource["id"] not in existing_ids]
        for resource in new_resources:
            session.add(model(**resource))
        session.commit()
        logger.info(f"Inserted {len(new_resources)} cached resources for model {model.__name__}")
    except Exception as e:
        logger.error(f"Error inserting cached resources for model {model.__name__}: {e}")

def getCachedResources(model):
    try:
        session = get_session()
        resources = session.query(model.id).all()
        logger.info(f"Retrieved {len(resources)} cached resources for model {model.__name__}")
        # Return only id and empty body
        return [{"id": r[0], "body": {}} for r in resources]
    except Exception as e:
        logger.error(f"Error retrieving cached resources for model {model.__name__}: {e}")

def insertCachedResource(model, id, body):
    try:
        session = get_session()
        resource = session.query(model).filter(model.id == id).first()
        if resource:
            # Update the body with the provided body dict
            resource.body = body
            logger.info(f"Updated cached resource for model {model.__name__} with id {id}")
        else:
            # Insert new resource
            resource = model(id=id, body=body)
            session.add(resource)
            logger.info(f"Inserted cached resource for model {model.__name__} with id {id}")
        session.commit()
    except Exception as e:
        logger.error(f"Error inserting cached resource for model {model.__name__} with id {id}: {e}")

def getCachedResourceById(model, id):
    try:
        session = get_session()
        resource = session.query(model).filter(model.id == id).first()
        if resource:
            logger.info(f"Retrieved cached resource for model {model.__name__} with id {id}")
        else:
            logger.warning(f"Cache miss for model {model.__name__} with id {id}")
        return resource
    except Exception as e:
        logger.error(f"Error retrieving cached resource for model {model.__name__} with id {id}: {e}")