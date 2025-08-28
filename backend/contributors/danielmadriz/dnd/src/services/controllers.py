"""
Orchestrates monster fetches with transparent caching.

Checks the local DB before hitting the upstream D&D API. On cache miss,
retrieves, persists, and returns the payload. All I/O is schema-validated;
errors are wrapped into typed HTTP responses with trace correlation
"""

import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))

from flask import request, jsonify
from ..domain.interfaces import IMonsterService
from ..helpers.exceptions import BaseError, ValidationError, ServiceError, NotFoundError


class MonsterController:

    def __init__(self, monster_service: IMonsterService, validator):

        self.monster_service = monster_service
        self.validator = validator
        self.logger = logging.getLogger(__name__)
    
    def get_monster(self):
        """
        Handle POST /get endpoint.
        Expected payload: {"monster_index": <index>}
        Returns:
            JSON response with monster data.
        """
        try:
            request_data = request.get_json()
            if not request_data:
                raise ValidationError("Request body must contain JSON data")
            
            # Validate request using Marshmallow schema
            try:
                validated_data = self.validator.validate_monster_request(request_data)
                monster_index = validated_data['monster_index']
            except Exception as e:
                raise ValidationError(f"Invalid monster request format: {str(e)}")
            
            self.logger.info(f"Get monster request validated successfully: {monster_index}")
            
            query_result = self.monster_service.get_monster(monster_index)
            
            include_cache_info = request.args.get('include_cache_info', 'false').lower() == 'true'

            # Serialize response using Marshmallow schema
            response_data = self.validator.serialize_monster_response(query_result.data)

            if include_cache_info:
                return jsonify({
                    'data': response_data,
                    'cache_info': {
                        'cached': query_result.is_cached,
                        'source': query_result.source
                    }
                }), 200

            self.logger.info(f"Monster {monster_index} returned successfully (cached: {query_result.is_cached})")
            
            return jsonify(response_data), 200
            
        except ValidationError as e:
            self.logger.warning(f"Validation error in get_monster: {str(e)}")
            return jsonify(e.to_dict()), e.status_code
            
        except ServiceError as e:
            self.logger.error(f"Service error in get_monster: {str(e)}")
            return jsonify(e.to_dict()), e.status_code
            
        except Exception as e:
            self.logger.error(f"Unexpected error in get_monster: {str(e)}")
            error_response = {
                'error': 'InternalServerError',
                'message': 'An unexpected error occurred',
                'status_code': 500
            }
            return jsonify(error_response), 500
    
    def list_monsters(self):
        """
        Handle POST /list endpoint.
        Expected payload: {"resource": "monsters"
        """
        try:
            request_data = request.get_json()
            if not request_data:
                raise ValidationError("Request body must contain JSON data")
            
            # Validate request using Marshmallow schema
            try:
                validated_data = self.validator.validate_monster_list_request(request_data)
            except Exception as e:
                raise ValidationError(f"Invalid monster list request format: {str(e)}")
            
            self.logger.info("Get monster list request validated successfully")
            
            query_result = self.monster_service.get_monster_list()
            
            include_cache_info = request.args.get('include_cache_info', 'false').lower() == 'true'

            # Serialize response using Marshmallow schema
            response_data = self.validator.serialize_monster_list_response(query_result.data)

            if include_cache_info:
                return jsonify({
                    'data': response_data,
                    'cache_info': {
                        'cached': query_result.is_cached,
                        'source': query_result.source
                    }
                }), 200

            self.logger.info(f"Monster list returned successfully (cached: {query_result.is_cached})")
            
            return jsonify(response_data), 200
            
        except ValidationError as e:
            self.logger.warning(f"Validation error in list_monsters: {str(e)}")
            return jsonify(e.to_dict()), e.status_code
            
        except ServiceError as e:
            self.logger.error(f"Service error in list_monsters: {str(e)}")
            return jsonify(e.to_dict()), e.status_code
            
        except Exception as e:
            self.logger.error(f"Unexpected error in list_monsters: {str(e)}")
            error_response = {
                'error': 'InternalServerError',
                'message': 'An unexpected error occurred',
                'status_code': 500
            }
            return jsonify(error_response), 500
    
    def health_check(self):
        """
        Handle GET /health endpoint for monitoring pourposes.
        Returns:
            JSON response with service health status
        """
        try:
            health_data = self._status_response()

            self.logger.debug("Health check requested")
            return jsonify(health_data), 200
            
        except Exception as e:
            self.logger.error(f"Error in health check: {str(e)}")
            error_response = {
                'error': 'InternalServerError',
                'message': 'Health check failed',
                'status_code': 500
            }
            return jsonify(error_response), 500
    
    def _status_response(self):
        health_data = {
                'status': 'healthy',
                'service': 'Forward Proxy Caching Service',
                'version': '1.0.0',
                'endpoints': {
                    'list': 'POST /list - Get monster list with caching',
                    'get': 'POST /get - Get specific monster with caching',
                    'health': 'GET /health - Service health check'
                }
            }
        
        return health_data

