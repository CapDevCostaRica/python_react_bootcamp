"""
Implements the API client interface for D&D5e API communication.
Handles HTTP requests, responses, and error handling.
"""
import requests
import logging
from typing import Optional, Dict, Any
from ..domain.interfaces import IMonsterApiClient
from ..helpers.exceptions import ExternalApiError

DND5E_API_BASE_URL = "https://www.dnd5eapi.co"
DEFAULT_TIMEOUT = 30

class DnD5eApiClient(IMonsterApiClient):
    
    def __init__(self, base_url: str = DND5E_API_BASE_URL, timeout: int = DEFAULT_TIMEOUT):

        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Forward-Proxy-Caching-Service/1.0',
            'Accept': 'application/json'
        })
    
    def get_monster(self, index: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/api/monsters/{index}"
            self.logger.info(f"Fetching monster from external API: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                monster_data = response.json()
                self.logger.info(f"Monster fetched successfully from external API: {index}")
                return monster_data
                
            elif response.status_code == 404:
                self.logger.warning(f"Monster not found in external API: {index}")
                return None
                
            else:
                self.logger.error(f"External API error {response.status_code}: {response.text}")
                raise ExternalApiError(
                    f"External API returned status {response.status_code}, for URL {url}",
                    details=f"Response: {response.text}"
                )
                
        except requests.exceptions.Timeout:
            self.logger.error(f"External API request timeout for monster: {index}, for URL {url}")
            raise ExternalApiError(
                f"External API {url} request timeout for monster: {index}",
                details="Request exceeded timeout limit"
            )
            
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"External API {url} connection error for monster {index}: {str(e)}")
            raise ExternalApiError(
                f"External API {url} connection failed for monster: {index}",
                details=f"Connection error: {str(e)}"
            )
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"External API  {url} request error for monster {index}: {str(e)}")
            raise ExternalApiError(
                f"External API  {url} request failed for monster: {index}",
                details=f"Request error: {str(e)}"
            )
            
        except Exception as e:
            self.logger.error(f"External API  {url} unexpected error fetching monster {index}: {str(e)}")
            raise ExternalApiError(
                f"External API  {url} unexpected error fetching monster: {index}",
                details=f"Error: {str(e)}"
            )
    
    def get_monster_list(self) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/api/monsters"
            self.logger.info(f"Fetching monster list from API: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                monster_list_data = response.json()
                self.logger.info("Monster list fetched successfully")
                return monster_list_data
                
            else:
                self.logger.error(f"API error {response.status_code}: {response.text}")
                raise ExternalApiError(
                    f"API returned status {response.status_code}",
                    details=f"Response: {response.text}"
                )
                
        except requests.exceptions.Timeout:
            self.logger.error("API request timeout for monster list")
            raise ExternalApiError(
                "API request timeout for monster list",
                details="Request exceeded timeout limit"
            )
            
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"API connection error for monster list: {str(e)}")
            raise ExternalApiError(
                "API connection failed for monster list",
                details=f"Connection error: {str(e)}"
            )
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error for monster list: {str(e)}")
            raise ExternalApiError(
                "API request failed for monster list",
                details=f"Request error: {str(e)}"
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error fetching monster list: {str(e)}")
            raise ExternalApiError(
                "Unexpected error fetching monster list",
                details=f"Error: {str(e)}"
            )
    
    def close(self):
        try:
            self.session.close()
            self.logger.info("API client session closed")
        except Exception as e:
            self.logger.warning(f"Error closing API client session: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 