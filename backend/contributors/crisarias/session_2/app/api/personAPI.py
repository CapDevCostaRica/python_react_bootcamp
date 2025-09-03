from marshmallow import ValidationError
from ..common import getFilterDictionary
from ..telemetry import logger
from .schemas import FilterSchema
from ..dataLayer.queryPerson import getPersonsDL

def getPersons(request):
    try:
        filter_dict = getFilterDictionary(request)
        logger.info(f"Received getPersons request. Filter: {filter_dict}")
        validatedFilter = FilterSchema().load(filter_dict)
        persons = getPersonsDL(validatedFilter)
        return persons
    except ValidationError as e:
        logger.error(f"Bad request from {request.remote_addr}: {e.messages}")
        raise ValueError(e.messages)
