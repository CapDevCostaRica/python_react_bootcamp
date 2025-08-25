"""
Este módulo inicializa el paquete de esquemas de Marshmallow
"""

# Importamos los esquemas para facilitar su acceso desde fuera
from app.schemas.marshmallow.monster_schema import MonsterRequestSchema

# Exportamos los esquemas explícitamente
__all__ = ['MonsterRequestSchema', 'MonsterListRequestSchema', 'MonsterListResponseModelSchema']
