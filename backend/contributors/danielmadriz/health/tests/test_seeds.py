import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from app.models import Person


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from seeds import process_people_data, process_physical_data, _read_csv_file_to_dataframe


class TestSeeds:
    
    def test_process_people_data_success(self):
        # Arrange
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None  # No existing person
        mock_session.add_all = Mock()
        mock_session.flush = Mock()
        mock_session.commit = Mock()
        
        mock_df = pd.DataFrame({
            'id': [1, 2],
            'full_name': ['John Doe', 'Jane Smith']
        })
        
        with patch('seeds._read_csv_file_to_dataframe', return_value=mock_df), \
             patch('seeds.mapper') as mock_mapper:
            
            mock_person1 = Mock()
            mock_person1.full_name = 'John Doe'
            mock_person1.id = None
            
            mock_person2 = Mock()
            mock_person2.full_name = 'Jane Smith'
            mock_person2.id = None
            
            mock_mapper.process_people_dataframe.return_value = [mock_person1, mock_person2]
            
            result = process_people_data(mock_session)
            
            # Assertions
            assert result == 2
            mock_session.add_all.assert_called_once()
            mock_session.flush.assert_called_once()
            mock_session.commit.assert_called_once()
            
            # Assert
            assert mock_person1.id == 1
            assert mock_person2.id == 2

    def test_process_people_data_empty_csv(self):
        mock_session = Mock()
        
        empty_df = pd.DataFrame()
        
        with patch('seeds._read_csv_file_to_dataframe', return_value=empty_df):
            result = process_people_data(mock_session)
            
            assert result == 0
            mock_session.add_all.assert_not_called()
            mock_session.commit.assert_not_called()

    def test_process_people_data_existing_person_skipped(self):
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = Mock()  # Existing person found
        mock_session.add_all = Mock()
        mock_session.flush = Mock()
        mock_session.commit = Mock()
        
        mock_df = pd.DataFrame({
            'id': [1],
            'full_name': ['John Doe']
        })
        
        with patch('seeds._read_csv_file_to_dataframe', return_value=mock_df), \
             patch('seeds.mapper') as mock_mapper:
            
            mock_person = Mock()
            mock_person.full_name = 'John Doe'
            mock_person.id = None
            
            mock_mapper.process_people_dataframe.return_value = [mock_person]
            
            result = process_people_data(mock_session)
            
            # Should return 0 since existing person was skipped
            assert result == 0
            mock_session.add_all.assert_not_called()
            mock_session.commit.assert_called_once()

    def test_process_people_data_large_batch(self):
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.add_all = Mock()
        mock_session.flush = Mock()
        mock_session.commit = Mock()
        
        large_data = {'id': list(range(1, 1003)), 'full_name': [f'Person {i}' for i in range(1, 1003)]}
        mock_df = pd.DataFrame(large_data)
        
        with patch('seeds._read_csv_file_to_dataframe', return_value=mock_df), \
             patch('seeds.mapper') as mock_mapper:
            
            mock_persons = []
            for i in range(1, 1003):
                mock_person = Mock()
                mock_person.full_name = f'Person {i}'
                mock_person.id = None
                mock_persons.append(mock_person)
            
            mock_mapper.process_people_dataframe.return_value = mock_persons
            
            result = process_people_data(mock_session)
            
            # Should process all 1002 records
            assert result == 1002
            # Should call add_all multiple times due to batching
            assert mock_session.add_all.call_count == 2  # 1000 + 2 remaining
            assert mock_session.flush.call_count == 2
            mock_session.commit.assert_called_once()

    def test_read_csv_file_to_dataframe_file_not_found(self):
        csv_path = Path("nonexistent_file.csv")
        
        result = _read_csv_file_to_dataframe(csv_path)
        
        assert result.empty
        assert isinstance(result, pd.DataFrame)

    def test_read_csv_file_to_dataframe_read_error(self):
        csv_path = Path("test_file.csv")
        
        with patch('pandas.read_csv', side_effect=Exception("Read error")):
            result = _read_csv_file_to_dataframe(csv_path)
            
            assert result.empty
            assert isinstance(result, pd.DataFrame)

    def test_process_physical_data_success(self):
        """Test successful processing of physical data"""
        mock_session = Mock()
        
        with patch('seeds._process_csv_data') as mock_process_csv_data:
            result = process_physical_data(mock_session)
            
            mock_process_csv_data.assert_called_once()
            call_args = mock_process_csv_data.call_args
            
            assert call_args[0][0] == mock_session
            assert call_args[0][1].name == "physical_data.csv"
            assert call_args[0][2] is not None
            assert call_args[0][3] == "physical profiles"
            assert call_args[0][4] is not None

    def test_process_physical_data_calls_process_csv_data(self):
        mock_session = Mock()
        
        with patch('seeds._process_csv_data') as mock_process_csv_data:
            result = process_physical_data(mock_session)
            
            mock_process_csv_data.assert_called_once()
            
            call_args = mock_process_csv_data.call_args[0]
            session_arg, csv_path_arg, process_func_arg, batch_name_arg, check_func_arg = call_args
            
            assert session_arg == mock_session
            assert csv_path_arg.name == "physical_data.csv"
            assert process_func_arg is not None  
            assert batch_name_arg == "physical profiles"
            assert check_func_arg is not None 
