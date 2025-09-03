import pytest
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from mappers.dataframe_mapper import DataFrameMapper

@pytest.fixture
def mapper():
    return DataFrameMapper()


def test_process_people_dataframe_empty_dataframe(mapper):
    empty_df = pd.DataFrame()
    result = mapper.process_people_dataframe(empty_df)
    assert result == []


def test_process_people_dataframe_single_person(mapper):
    df = pd.DataFrame({
        'id': [1],
        'full_name': ['John Doe']
    })
    result = mapper.process_people_dataframe(df)
    assert len(result) == 1
    assert result[0].full_name == 'John Doe'


def test_process_people_dataframe_with_whitespace(mapper):
    df = pd.DataFrame({
        'id': [1, 2],
        'full_name': ['  John Doe  ', 'Jane Smith\n']
    })
    result = mapper.process_people_dataframe(df)
    assert len(result) == 2
    assert result[0].full_name == 'John Doe'
    assert result[1].full_name == 'Jane Smith'


@pytest.mark.parametrize("input_value,expected", [
    ("  hello  ", "hello"),
    (None, ""),
    ("", ""),
    (123, "123"),
    (123.45, "123.45"),
    ("  test  ", "test"),
    ("\n\nvalue\n\n", "value"),
    (0, "0"),
    (0.0, "0.0"),
])
def test_convert_to_string_basic(mapper, input_value, expected):
    assert mapper._convert_to_string(input_value) == expected


@pytest.mark.parametrize("input_value,expected", [
    ("123", 123),
    (123, 123),
    (None, None),
    ("", None),
    ("abc", None),
    ("123.45", 123),
    ("0", 0),
    (0, 0),
    ("0.0", 0),
    ("999.99", 999),
    ("invalid", None),
    ("   ", None),
])
def test_convert_to_integer_basic(mapper, input_value, expected):
    assert mapper._convert_to_integer(input_value) == expected


if __name__ == '__main__':
    pytest.main([__file__, '-v'])