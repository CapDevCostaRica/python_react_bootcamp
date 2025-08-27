"""
Provides consistent error handling structure across all layers.
    Args:
    message: Human-readable error message
    details: Technical details for debugging
    status_code: HTTP status code for API responses
"""


class BaseError(Exception):
    
    def __init__(self, message: str, details: str = None, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.details = details
        self.status_code = status_code
    
    def to_dict(self) -> dict:
        error_dict = {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code
        }
        
        if self.details:
            error_dict["details"] = self.details
        
        return error_dict


class ValidationError(BaseError):

    def __init__(self, message: str, details: str = None):
        super().__init__(message, details, status_code=400)


class ServiceError(BaseError):    

    def __init__(self, message: str, details: str = None):
        super().__init__(message, details, status_code=500)


class NotFoundError(BaseError):
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message, details, status_code=404)
