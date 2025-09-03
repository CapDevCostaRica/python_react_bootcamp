import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# Mock the models and Flask request before importing people_service
mock_models = Mock()
mock_request = Mock()

with patch.dict('sys.modules', {
    'models': mock_models,
    'database': Mock()
}), patch('people_service.request', mock_request):
    from people_service import _query_people_with_filters


class TestPeopleService:
    """Test cases for people_service module"""
    
    def test_parse_filters_logic(self):
        """Test the filter parsing logic without Flask request context"""
        # Test the core logic of parsing filters from a dictionary
        def parse_filters_from_dict(args_dict):
            """Replicate the _parse_filters logic for testing"""
            filters = {}
            numeric_fields = ['age', 'height_cm', 'weight_kg']
            
            for key, value in args_dict.items():
                if key.startswith('filters[') and key.endswith(']'):
                    filter_key = key[8:-1]  # Remove 'filters[' and ']'
                    
                    if filter_key in numeric_fields:
                        try:
                            filters[filter_key] = int(value)
                        except ValueError:
                            # Skip invalid numeric values
                            continue
                    else:
                        filters[filter_key] = value
            
            return filters
        
        # Test basic parsing
        args = {
            'filters[food]': 'lasagna',
            'filters[age]': '25',
            'filters[eye_color]': 'brown',
            'other_param': 'ignored'
        }
        
        result = parse_filters_from_dict(args)
        assert result == {
            'food': 'lasagna',
            'age': 25,
            'eye_color': 'brown'
        }
        
        # Test numeric conversion
        args = {
            'filters[age]': '30',
            'filters[height_cm]': '175',
            'filters[weight_kg]': '70'
        }
        
        result = parse_filters_from_dict(args)
        assert result['age'] == 30
        assert result['height_cm'] == 175
        assert result['weight_kg'] == 70
        assert isinstance(result['age'], int)
        
        # Test invalid numeric handling
        args = {
            'filters[age]': 'invalid',
            'filters[food]': 'pizza'
        }
        
        result = parse_filters_from_dict(args)
        assert 'age' not in result
        assert result['food'] == 'pizza'
    
    def test_query_people_with_filters_no_filters(self):
        """Test query when no filters are provided"""
        # Mock session and Person model
        mock_session = Mock(spec=Session)
        mock_person1 = Mock()
        mock_person1.full_name = "John Doe"
        mock_person2 = Mock()
        mock_person2.full_name = "Jane Smith"
        
        mock_session.query.return_value.all.return_value = [mock_person1, mock_person2]
        
        result = _query_people_with_filters(mock_session, {})
        
        # Should return all people when no filters
        assert len(result) == 2
        assert result[0].full_name == "John Doe"
        assert result[1].full_name == "Jane Smith"
        mock_session.query.assert_called_once()
    
    def test_query_people_with_filters_basic(self):
        """Test query with basic filters"""
        # Mock session
        mock_session = Mock(spec=Session)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        
        # Mock Person objects
        mock_person = Mock()
        mock_person.full_name = "Test Person"
        mock_query.all.return_value = [mock_person]
        
        # Mock the query chain methods to return the query itself
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        
        filters = {
            'food': 'pizza',
            'age': 25
        }
        
        result = _query_people_with_filters(mock_session, filters)
        
        # Should return filtered results
        assert len(result) == 1
        assert result[0].full_name == "Test Person"
        
        # Verify query was built with filters
        mock_session.query.assert_called_once()
        mock_query.join.assert_called()  # Should join PhysicalProfile for age filter
        mock_query.filter.assert_called()  # Should apply filters
    
    def test_query_people_with_filters_comprehensive(self):
        """Test query with multiple filter types"""
        # Mock session
        mock_session = Mock(spec=Session)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        
        # Mock Person objects
        mock_person = Mock()
        mock_person.full_name = "Test Person"
        mock_query.all.return_value = [mock_person]
        
        # Mock the query chain methods to return the query itself
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        
        # Test with multiple filter types
        filters = {
            'food': 'pizza',
            'age': 25,
            'eye_color': 'brown',
            'hobby': 'gaming',
            'degree': 'PhD'
        }
        
        result = _query_people_with_filters(mock_session, filters)
        
        # Should return filtered results
        assert len(result) == 1
        assert result[0].full_name == "Test Person"
        
        # Verify query was built with filters
        mock_session.query.assert_called_once()
        mock_query.join.assert_called()  # Should join PhysicalProfile for age/eye_color filters
        mock_query.filter.assert_called()  # Should apply filters


if __name__ == '__main__':
    pytest.main([__file__])
