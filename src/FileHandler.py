"""
This module provides basic functionality to convert data stored in .xlsx or .csv files into python
lists.
"""
# standard library imports
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path

# related third party imports
import pandas as pd

# local imports


logger = logging.getLogger("FileHandler")


class FileExtensions(Enum):
    """Enum class that has all valid file extension names and suffixes."""
    EXCEL = "XLSX"
    CSV = "CSV"


def is_extension_supported(file_path: str) -> bool:
    """Check if the file extension at the given path is supported.

    :param file_path: Path pointing to the file.
    :type file_path: str
    :return: True if supported, False otherwise.
    :rtype: bool
    """
    suffix = Path(file_path).suffix
    if suffix == "":
        return False
    extension = suffix.split(".")[1]
    return extension.upper() in [valid_extension.value for valid_extension in FileExtensions]


def read_file(file_path: str) -> pd.DataFrame:
    """Read a `.csv` or `.xlsx` file from the given path and return it as a `pd.DataFrame`.

    Uses pathlib's `is_file()` method to ensure there is a file at the given path.
    Then tries to obtain the file's suffix and checks for `.csv` or `.xlsx` formats,
    for which the corresponding pandas read method is called.

    :param file_path: Path to the file to be read.
    :type file_path: str
    :raises FileNotFoundError: If no file exists at `file_path`.
    :raises ValueError: If `file_path` has no suffix.
    :raises TypeError: If the file is not either an Excel table or CSV file.
    :return: A `pd.DataFrame` containing all information that is read from the excel or csv file.
    :rtype: pd.DataFrame
    """
    if not Path(file_path).is_file():
        raise FileNotFoundError("Invalid Path; no file at destination.")

    suffix = Path(file_path).suffix
    if suffix == "":
        raise ValueError("No file extension found at path.")

    if suffix.split(".")[1].upper() == FileExtensions.EXCEL.value:
        data_frame = pd.read_excel(file_path)
    elif suffix.split(".")[1].upper() == FileExtensions.CSV.value:
        try:
            data_frame = pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            logger.warning("FileHandler got an empty CSV file to read. Returning empty DataFrame.")
            data_frame = pd.DataFrame()
    else:
        raise TypeError("Invalid file extension.")

    return data_frame


def dataframe_tolist(data_frame: pd.DataFrame) -> list[list[float | int]]:
    """Convert a `pd.DataFrame` to a list of lists containing its values.

    :param data_frame: `DataFrame` to be converted.
    :type data_frame: pd.DataFrame
    :raises ValueError: If the `data_frame` is None, empty, contains empty cells, or non-numeric values.
    :return: List of lists containing the DataFrame's values.
    :rtype: list[list[float | int]]
    """
    if data_frame is None:
        raise ValueError("DataFrame can't be None.")

    if data_frame.empty:
        raise ValueError("DataFrame is empty.")

    if data_frame.isnull().values.any():
        raise ValueError("DataFrame has empty cells.")

    column_names = data_frame.columns.tolist()

    # if the names of the columns are ever relevant
    # first_row = [name for name in column_names]

    data_list = [data_frame[name].tolist() for name in column_names]

    if not all(isinstance(x, (int, float)) for inner in data_list for x in inner):
        raise ValueError("Provided data needs to only consist of numbers.")

    return data_list


def get_valid_filename() -> str:
    """Create a valid, hopefully non-duplicate, string to use as a file name.

    :return: Stringified time from `datetime.now()` in the form of `%Y-%m-%d-result-from-%Hh%Mm`.
    :rtype: str
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d-result-from-%Hh%Mm")


def write_file(
    data_frame: pd.DataFrame,
    file_format: FileExtensions = FileExtensions.EXCEL,
    destination: str = "./res/"
    ) -> None:
    """Write the provided `pd.DataFrame` as either `.xlsx` or `.csv` to the `./res/` directory.

    If there is no `./res/` directory relative to where the program was started from,
    that directory will be created.

    :param data_frame: The data frame to be written.
    :type data_frame: pd.DataFrame
    :param file_format: Format of the written file, defaults to `FileExtensions.EXCEL`.
    :type file_format: FileExtensions, optional
    :param destination: Destination directory, default to "./res/".
    :raises TypeError: If `file_format` was neither Excel nor CSV.
    """
    relative_path = Path(destination)

    relative_path.mkdir(exist_ok=True)

    file_name = get_valid_filename()

    if file_format == FileExtensions.EXCEL:
        file_name += ".xlsx"
        path = relative_path / file_name
        data_frame.to_excel(path, index=False, header=False)
        logger.debug(
            f"{file_format} file was written to:"
            f"  {path}"
        )
    elif file_format == FileExtensions.CSV:
        file_name += ".csv"
        path = relative_path / file_name
        data_frame.to_csv(path, index=False, header=False, sep="\t")
        logger.debug(
            f"{file_format} file was written to:"
            f"  {path}"
        )
    else:
        logger.error(f"File format was: {file_format} but only 'EXCEL' and 'CSV' are supported")
        raise TypeError("Can't write to unknown file extension")
