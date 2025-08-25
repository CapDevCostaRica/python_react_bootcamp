# Add validators here, for example using Marshmallow schemas
class MonsterSchema:
    """Basic validation schema for Monster data"""
    
    @staticmethod
    def validate(data):
        # Basic validation example
        errors = {}
        
        if 'name' not in data:
            errors['name'] = ['Name is required']
        
        if errors:
            return False, errors
            
        return True, None
