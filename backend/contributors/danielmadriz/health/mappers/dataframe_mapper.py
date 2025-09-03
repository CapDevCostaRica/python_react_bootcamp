import pandas as pd
from typing import Dict, List, Any, Type, Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))
from models import Person, PhysicalProfile, FavoriteFood, Hobby, FamilyRelation, Study


class DataFrameMapper:
    """
    Mapper class for transforming pandas DataFrames to model objects.
    """

    def __init__(self):
        self.field_mappings = {
            'physical_profile': {
                'person_id': 'person_id',
                'eye_color': 'eye_color',
                'hair_color': 'hair_color',
                'age': 'age',
                'height_cm': 'height_cm',
                'weight_kg': 'weight_kg',
                'nationality': 'nationality'
            },
            'favorite_food': {
                'person_id': 'person_id',
                'food': 'food'
            },
            'hobby': {
                'person_id': 'person_id',
                'hobby': 'hobby'
            },
            'family_relation': {
                'person_id': 'person_id',
                'relation': 'relation',
                'name': 'name'
            },
            'study': {
                'person_id': 'person_id',
                'degree': 'degree',
                'institution': 'institution'
            }
        }
        
        self.model_classes = {
            'physical_profile': PhysicalProfile,
            'favorite_food': FavoriteFood,
            'hobby': Hobby,
            'family_relation': FamilyRelation,
            'study': Study
        }
        
        self.integer_fields = {'age', 'height_cm', 'weight_kg'}
    
    def process_people_dataframe(self, df: pd.DataFrame) -> List[Person]:
        return [Person(full_name=self._convert_to_string(row['full_name'])) for _, row in df.iterrows()]
    
    def process_physical_dataframe(self, df: pd.DataFrame) -> List[PhysicalProfile]:
        return self._process_related_dataframe(
            df, 'physical_profile'
        )
    
    def process_favorite_food_dataframe(self, df: pd.DataFrame) -> List[FavoriteFood]:
        return self._process_related_dataframe(
            df, 'favorite_food'
        )
    
    def process_hobby_dataframe(self, df: pd.DataFrame) -> List[Hobby]:
        return self._process_related_dataframe(
            df, 'hobby'
        )
    
    def process_family_relation_dataframe(self, df: pd.DataFrame) -> List[FamilyRelation]:
        return self._process_related_dataframe(
            df, 'family_relation'
        )
    
    def process_study_dataframe(self, df: pd.DataFrame) -> List[Study]:
        return self._process_related_dataframe(
            df, 'study'
        )
    
    def _process_related_dataframe(
        self, 
        df: pd.DataFrame, 
        entity_type: str
    ) -> List[Any]:
        
        self._validate_entity_type(entity_type)
        
        field_mapping = self.field_mappings[entity_type]
        model_class = self.model_classes[entity_type]
        
        objects = []
        for _, row in df.iterrows():
            # Since CSV ID = Database ID, we can use the CSV person_id directly
            person_id = int(row['person_id'])
            
            kwargs = {'person_id': person_id}
            for df_column, model_attr in field_mapping.items():
                if df_column != 'person_id':
                    value = row[df_column]
                    kwargs[model_attr] = self._convert_field_value(value, model_attr)
            
            objects.append(model_class(**kwargs))
        
        return objects
    
    def _validate_entity_type(self, entity_type: str) -> None:
        if entity_type not in self.field_mappings:
            supported_types = ', '.join(self.field_mappings.keys())
            raise ValueError(
                f"Unknown entity type: '{entity_type}'. "
                f"Supported types: {supported_types}"
            )
    
    def _convert_field_value(self, value: Any, model_attr: str) -> Any:
        if model_attr in self.integer_fields:
            return self._convert_to_integer(value)
        else:
            return self._convert_to_string(value)
    
    def _convert_to_integer(self, value: Any) -> Optional[int]:
        try:
            if value is None or pd.isna(value):
                return None
            # Handle float strings like "123.45"
            if isinstance(value, str) and '.' in value:
                return int(float(value))
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _convert_to_string(self, value: Any) -> str:
        if value is None or pd.isna(value):
            return ''
        return str(value).strip()
    
    def get_supported_entity_types(self) -> List[str]:
        return list(self.field_mappings.keys())
    
    def add_entity_type(self, entity_type: str, field_mapping: Dict[str, str], model_class: Type):
        self.field_mappings[entity_type] = field_mapping
        self.model_classes[entity_type] = model_class
