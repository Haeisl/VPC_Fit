import pytest
import pandas as pd
from src.FileHandler import *

# Fixture for creating temporary file paths

@pytest.fixture
def temp_file_path_xlsx(tmp_path):
    file_path = tmp_path / "test.xlsx"
    return file_path

@pytest.fixture
def temp_file_path_csv(tmp_path):
    file_path = tmp_path / "test.csv"
    return file_path

# Fixture for creating temporary DataFrame
@pytest.fixture
def temp_dataframe():
    return pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

# Test cases for is_extension_supported function
@pytest.mark.parametrize("file_path, expected", [
    ("test.xlsx", True),
    ("test.csv", True),
    ("test.txt", False),
    ("noextension", False)
])
def test_is_extension_supported(file_path, expected):
    assert is_extension_supported(file_path) == expected

# Test cases for read_file function
def test_read_file_excel(temp_file_path_xlsx):
    pd.DataFrame({"A": [1, 2, 3]}).to_excel(temp_file_path_xlsx, index=False)
    assert isinstance(read_file(temp_file_path_xlsx), pd.DataFrame)

def test_read_file_csv(temp_file_path_csv):
    pd.DataFrame({"A": [1, 2, 3]}).to_csv(temp_file_path_csv, index=False)
    assert isinstance(read_file(temp_file_path_csv), pd.DataFrame)

def test_read_file_invalid_file(tmp_path):
    file_path = tmp_path / "test.txt"
    with pytest.raises(FileNotFoundError):
        read_file(file_path)

# Test cases for dataframe_tolist function
def test_dataframe_tolist(temp_dataframe):
    expected = [[1, 2, 3], [4, 5, 6]]
    assert dataframe_tolist(temp_dataframe) == expected

def test_dataframe_tolist_empty():
    with pytest.raises(ValueError):
        dataframe_tolist(pd.DataFrame())

# Test cases for write_file function
def test_write_file_excel(temp_dataframe, tmp_path):
    file_path = tmp_path / "test.xlsx"
    write_file(temp_dataframe, FileExtensions.EXCEL, file_path)
    assert file_path.exists()

def test_write_file_csv(temp_dataframe, tmp_path):
    file_path = tmp_path / "test.csv"
    write_file(temp_dataframe, FileExtensions.CSV, file_path)
    assert file_path.exists()

def test_write_file_invalid_format(temp_dataframe, tmp_path):
    with pytest.raises(TypeError):
        write_file(temp_dataframe, "invalid_format") # type: ignore

def test_read_empty_excel_file(tmp_path):
    file_path = tmp_path / "empty.xlsx"
    pd.DataFrame().to_excel(file_path, index=False)
    assert read_file(file_path).empty

def test_read_empty_csv_file(tmp_path):
    file_path = tmp_path / "empty.csv"
    pd.DataFrame().to_csv(file_path, index=False)
    assert read_file(file_path).empty

# Test reading a file with only headers but no data
def test_read_file_with_headers_only(tmp_path):
    file_path = tmp_path / "headers_only.csv"
    pd.DataFrame(columns=["A", "B"]).to_csv(file_path, index=False)
    assert read_file(file_path).empty

# Test reading a file with special characters in the data
def test_read_file_with_special_characters(tmp_path):
    file_path = tmp_path / "special_characters.csv"
    data = {"A": ["$100", "%200", "#300"]}
    pd.DataFrame(data).to_csv(file_path, index=False)
    assert isinstance(read_file(file_path), pd.DataFrame)

# Test writing an empty DataFrame to both Excel and CSV formats
def test_write_empty_dataframe(tmp_path):
    file_path_excel = tmp_path / "empty.xlsx"
    file_path_csv = tmp_path / "empty.csv"
    empty_df = pd.DataFrame()
    write_file(empty_df, FileExtensions.EXCEL, file_path_excel)
    write_file(empty_df, FileExtensions.CSV, file_path_csv)
    assert file_path_excel.exists()
    assert file_path_csv.exists()
