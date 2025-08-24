import logging
import os
import sys


from requests import codes
from dnd.validators import input_list_schema, input_get_schema, output_list_schema, output_get_schema
from dnd.api import API
from marshmallow import ValidationError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from database import get_session
from models import Monsterscastroulloaaaron, AllMonsterscastroulloaaaron


class Service:
    def __init__(self, api=API()):
        self._logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self._api = api

    def list(self, payload: dict):
        try:
            input_list_schema.load(payload)
        except ValidationError as e:
            return {'errors': e.messages}, codes.bad_request
        try:
            return self._fetch_list(), codes.ok
        except:
            self._logger.error('Error on fetching all the monsters the data from the database and API')
            return {'error': 'Error fetching the data'}, codes.internal_server_error

    def _fetch_list(self):
        session = get_session()
        try:
            data = session.query(AllMonsterscastroulloaaaron).first()
            if data:
                session.close()
                return data.json_data
        except:
            self._logger.warning('Error fetching the data from the database')

        data = self._api.list()
        try:
            output_list_schema.load(data, many=True)
        except ValidationError as e:
            self._logger.error(f'Error validating the data from the API: {e.messages}')
            session.close()
            raise e
        try:
            session.add(AllMonsterscastroulloaaaron(json_data=data))
            session.commit()
            session.close()
        except Exception as e:
            self._logger.warning(f'Error saving the monsters data to the database: {e}')
        finally:
            return data

    def get(self, payload: dict):
        try:
            input_get_schema.load(payload)
        except ValidationError as e:
            return {'error': e.messages}, codes.bad_request
        try:
            return self._fetch_get(payload['monster_index']), codes.ok
        except:
            self._logger.error(f'Error on fetching the {payload['monster_index']} data from the database and API')
            return {'error': f'Error fetching the data {payload['monster_index']}'}, codes.internal_server_error

    def _fetch_get(self, index: str) -> dict:
        session = get_session()
        try:
            data = session.query(Monsterscastroulloaaaron).filter_by(id=index).first()
            if data:
                session.close()
                return data.json_data
        except:
            self._logger.warning(f'Error fetching the data for index {index} from the database')

        data = self._api.get(index)
        try:
            output_get_schema.load(data)
        except ValidationError as e:
            self._logger.error(f'Error validating the data from the API for the monster {index}: {e.messages}')
            session.close()
            raise e
        try:
            session.add(Monsterscastroulloaaaron(id=index, json_data=data))
            session.commit()
            session.close()
        except Exception as e:
            self._logger.warning(f'Error saving the monster {index} to the database: {e}')
        finally:
            return data
