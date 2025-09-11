from marshmallow import ValidationError
from ..common import getFilterDictionary
from ..telemetry import logger
from .schemas import FilterSchema
from ..dataLayer.queryPerson import (
    getPersonsDL,
    getPersonThatEatFoodsDL,
    getMostCommonFoodDL,
    getAverageWeightAbove70ByHairDL,
    getAverageWeightByNationalityAndHairDL,
    getTopOldestByNationalityDL,
    getTopPeopleByHobbiesCountDL,
    getAverageHeightByNationalityAndGeneralDL
)

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

def getSushiAndRamenCountReport():
    logger.info("Received getSushiAndRamenPersonReport request.")
    personsCount = getPersonThatEatFoodsDL(["sushi", "ramen"])
    return personsCount

def getMostCommonFoodReport():
    logger.info("Received getMostCommonFoodReport request.")
    mostCommonFood = getMostCommonFoodDL()
    return mostCommonFood

def getAvgWeightAbove70HairReport():
    logger.info("Received getAvgWeightAbove70HairReport request.")
    avgWeightByHair = getAverageWeightAbove70ByHairDL()
    return avgWeightByHair

def getAverageWeightByNationalityAndHairReport():
    logger.info("Received getAverageWeightByNationalityAndHairReport request.")
    avgWeightByNationalityAndHair = getAverageWeightByNationalityAndHairDL()
    return avgWeightByNationalityAndHair

def getTopOldestByNationalityReport():
    logger.info("Received getTopOldestByNationalityReport request.")
    topOldestByNationality = getTopOldestByNationalityDL()
    return topOldestByNationality

def getTopPeopleByHobbiesCountReport():
    logger.info("Received getTopPeopleByHobbiesCountReport request.")
    topPeopleByHobbiesCount = getTopPeopleByHobbiesCountDL()
    return topPeopleByHobbiesCount

def getAverageHeightByNationalityAndGeneralReport():
    logger.info("Received getAverageHeightByNationalityAndGeneralReport request.")
    avgHeightByNationalityAndGeneral = getAverageHeightByNationalityAndGeneralDL()
    return avgHeightByNationalityAndGeneral
