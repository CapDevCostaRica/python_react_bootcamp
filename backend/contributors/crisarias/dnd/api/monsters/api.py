from services.telemetry import setupLogger
from marshmallow import ValidationError
from .schemas import GetMonsterSchema, ListMonstersSchema, MonstersCrisariasSchema
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../framework')))
from models import MonstersCrisarias
from services.caching import getCachedResources, getCachedResourceById
from services.dnd import getMonsterById, getMonsters

logger = setupLogger()

def getMonster(request):
    try:
        data = request.get_json()
        logger.info(f"Received getMonster request data: {data}")
        validated = GetMonsterSchema().load(data)
        monster_id = validated["monster_index"]
        cachingResponse = getCachedResourceById(MonstersCrisarias, monster_id)
        if cachingResponse is None or cachingResponse == {}:
            logger.info(f"Cache miss for monster_id {monster_id}")
            data, code = getMonsterById(monster_id)
            if code != 200:
                if code == 404:
                    logger.warning(f"Monster_id {monster_id} not found")
                    return None, 404
                raise ConnectionError(f"Cannot fetch monster_id {monster_id} upstream service unavailable")
            validatedData = MonstersCrisariasSchema().load(data)
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
        logger.info(f"Received listMonsters request data: {data}")
        ListMonstersSchema().load(data)
        cachingResponse = getCachedResources(MonstersCrisarias)
        if cachingResponse is None or len(cachingResponse) == 0:
            logger.info(f"Cache miss for monsters list")
            data, code = getMonsters()
            if code != 200:
                raise ConnectionError(f"Cannot fetch monsters upstream service unavailable")
            validatedData = [MonstersCrisariasSchema().load(item) for item in data]
            return validatedData, 200
        else:
            logger.info(f"Cache hit for monsters")
            validatedCached = [MonstersCrisariasSchema().load(item) for item in data]
            return validatedCached, 200
    except ValidationError as e:
        logger.error(f"Bad request from {request.remote_addr}: {e.messages}")
        raise ValueError(e.messages)