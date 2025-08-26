from services.telemetry import setupLogger
from marshmallow import ValidationError
from .schemas import GetMonsterSchema, ListMonstersSchema, MonstersCrisariasSchema, MonstersCrisariasSimplifiedSchema
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../framework')))
from models import MonstersCrisarias
from services.dnd_caching import getCachedResources, getCachedResourceByIndex, insertCachedResources, upsertCachedResource
from services.dnd import getMonsterById, getMonsters

logger = setupLogger()

def getMonster(request):
    try:
        data = request.get_json()
        logger.info(f"Received getMonster request data: {data}")
        validated = GetMonsterSchema().load(data)
        monster_id = validated["monster_index"]
        cachingResponse = getCachedResourceByIndex(MonstersCrisarias, monster_id)
        if cachingResponse is None or cachingResponse == {}:
            logger.info(f"Cache miss for monster_id {monster_id}")
            data, code = getMonsterById(monster_id)
            if code != 200:
                if code == 404:
                    logger.warning(f"Monster_id {monster_id} not found")
                    return None, 404
                raise ConnectionError(f"Cannot fetch monster_id {monster_id} upstream service unavailable")
            validatedData = MonstersCrisariasSchema().load(data)
            logger.info(f"Insert monster_id {monster_id} into cache")
            upsertCachedResource(MonstersCrisarias, monster_id, validatedData)
            return validatedData, 200
        else:
            logger.info(f"Cache hit for monster_id {monster_id}")
            validatedCached = MonstersCrisariasSchema().load(cachingResponse)
            return validatedCached, 200
    except ValidationError as e:
        logger.error(f"Bad request from {request.remote_addr}: {e.messages}")
        raise ValueError(e.messages)

def listMonsters(request):
    try:
        data = request.get_json()
        ListMonstersSchema().load(data)
        cachingResponse = getCachedResources(MonstersCrisarias)
        if cachingResponse is None or len(cachingResponse) == 0:
            logger.info(f"Cache miss for monsters list")
            data, code = getMonsters()
            if code != 200:
                raise ConnectionError(f"Cannot fetch monsters upstream service unavailable")            
            validatedData = [MonstersCrisariasSimplifiedSchema().load(item) for item in data]
            return validatedData, 200
        else:
            logger.info(f"Cache hit for monsters")
            validatedCached = [MonstersCrisariasSimplifiedSchema().load(item) for item in cachingResponse]
            return validatedCached, 200
    except ValidationError as e:
        logger.error(f"Bad request from {request.remote_addr}: {e.messages}")
        raise ValueError(e.messages)
    
def warmCache (request):
    try:
        logger.info(f"Warm cache requested")
        data = request.get_json()
        validatedData = [MonstersCrisariasSchema().load(item) for item in data]
        insertCachedResources(MonstersCrisarias, validatedData)
        logger.info(f"The data was added to the cache: {validatedData}")
        return {"message": "Cache warmed successfully"}, 200
    except ValidationError as e:
        logger.error(f"Bad request from {request.remote_addr}: {e.messages}")
        raise ValueError(e.messages)