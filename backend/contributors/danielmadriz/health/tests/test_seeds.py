import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Mock the database module before importing seeds
with patch.dict('sys.modules', {
    'database': Mock(),
    'framework.database': Mock(),
    'framework.seeds': Mock()  # Mock the framework seeds to avoid conflicts
}):
    # Add the parent directory to path to import local seeds.py
    parent_dir = os.path.join(os.path.dirname(__file__), '..')
    sys.path.insert(0, parent_dir)  # Insert at beginning to prioritize local seeds
    
    # Import the local seeds module
    import seeds
    from seeds import process_people_data, process_physical_data, _read_csv_file_to_dataframe


class TestSeeds:

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

 
