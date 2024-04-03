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
from src.ModelData import ModelData


logger = logging.getLogger("FileHandler")


class FileExtensions(Enum):
    """Enum class that has all valid file extension names and suffixes."""
    EXCEL = "XLSX"
    CSV = "CSV"


def is_extension_supported(file_path: str) -> bool:
    """Function to determine whether a file extension at the given path is supported.

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
    """Function to read a ``.csv`` or ``.xlsx`` file from a given path
    and return its value as a ``pd.DataFrame``.

    Uses pathlib's ``is_file()`` method to assure there is a file at the given path.
    Then tries to obtain the file's suffix and checks for ``.csv`` or ``.xlsx`` formats,
    for which the corresponding pandas read method is called.

    :param file_path: String for path to the file that is to be read.
    :type file_path: str
    :raises FileNotFoundError: If there is no file at ``file_path``\
    according to pathlib's ``is_file()`` method.
    :raises ValueError: If the file at the provided path has no suffix.
    :raises TypeError: If the file at the provided path is not either an excel table or csv file.
    :return: A ``pd.DataFrame`` containing all information that is read from the excel or csv file.
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
    """Takes a ``pd.DataFrame`` and returns a ``list`` containing a separate ``list``
    for every column in the original DataFrame. The values in the inner ``list`` are the ``int``
    or ``float`` values that are in this column.

    :param data_frame: The ``pd.DataFrame`` that is to be read.
    :type data_frame: pd.DataFrame
    :raises ValueError: If the provided data frame is ``None``.
    :raises ValueError: If the provided data frame is empty.
    :raises ValueError: If there are empty cells in the data frame.
    :raises ValueError: If there are non-``int`` or non-``float`` values in the data.
    :return: A list of lists of each column's data.
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


def create_dataframe_from_for(
    model_data: ModelData,
    format: FileExtensions = FileExtensions.EXCEL
) -> pd.DataFrame:
    """Creates a ``pd.DataFrame`` for the specified ``format``, i.e. either Excel or CSV.
    The data frame contains information about the user inputs into the program and what the program
    made of those. It also contains the fit of the model if possible. If no fitted model string was
    given, a warning will be logged and the field in the data frame will read 'N/A'.

    :param fitted_model: The fitted model as a ``str``.
    :type fitted_model: str | None
    :param fitted_consts: The dictionary of the constants as keys of type ``str`` and their value\
    as ``float``. Alternatively just a string containing the same information.
    :type fitted_consts: dict[str, float] | str | None
    :param model: The model the program worked with, defaults to "f(t) = ..."
    :type model: str, optional
    :param user_input_model: The exact model the user entered, defaults to "f(t) = ..."
    :type user_input_model: str, optional
    :param parameter: The independent variable the program worked with, defaults to ["..."]
    :type parameter: list[str], optional
    :param user_input_parameter: The exact independent variables the user entered, defaults to "..."
    :type user_input_parameter: str, optional
    :param consts: The constants the program worked with, defaults to ["..."]
    :type consts: list[str], optional
    :param user_input_consts: The exact constants the user entered, defaults to ["..."]
    :type user_input_consts: list[str], optional
    :param user_input_path: The path to the data the user provided, defaults to "path/to/data"
    :type user_input_path: str, optional
    :param format: The format for which the data frame is constructed, defaults to FileExtensions.EXCEL
    :type format: FileExtensions, optional
    :return: A data frame containing all input and output information.
    :rtype: pd.DataFrame
    """
    if model_data.fitted_model is None:
        logger.warning(f"Did not get a fitted model string.")
        fitted_model = "N/A"
        fitted_consts = "N/A"

    if format == FileExtensions.EXCEL:
        data = pd.DataFrame(
            index=range(1, 9),
            columns=["A", "B", "C", "D", "E"]
        )

        data.at[1,"A"]  = "Fitted Model:"
        data.at[1,"B"]  = fitted_model
        data.at[2,"A"]  = "Fitted Constants:"
        data.at[2,"B"]  = fitted_consts
        data.at[4,"A"]  = "Interpreted Data"
        data.at[4,"D"]  = "Raw Data"
        data.at[5,"A"]  = "Model:"
        data.at[5,"B"]  = model_data.model
        data.at[5,"D"]  = "Entered Model:"
        data.at[5,"E"]  = model_data.user_input_model
        data.at[6,"A"]  = "Independent Var:"
        data.at[6,"B"]  = model_data.parameter
        data.at[6,"D"]  = "Entered Independent Var:"
        data.at[6,"E"]  = model_data.user_input_parameter
        data.at[7,"A"] = "Constants:"
        data.at[7,"B"] = model_data.consts
        data.at[7,"D"] = "Entered Constants:"
        data.at[7,"E"] = model_data.user_input_consts
        data.at[8,"D"] = "Entered Data:"
        data.at[8,"E"] = model_data.user_input_path

    elif format == FileExtensions.CSV:
        data = pd.DataFrame({
            "1": ["Fitted Model:",  "Interpreted",          "Raw"                       ],
            "2": [fitted_model,     "Model:",               "Entered Model:"            ],
            "3": [None,             model_data.model,       model_data.user_input_model            ],
            "4": [None,             "Independent Var:",     "Entered Independent Var:"  ],
            "5": [None,             model_data.parameter,   model_data.user_input_parameter        ],
            "6": [None,             "Constants:",           "Entered Constants:"        ],
            "7": [None,             model_data.consts,      model_data.user_input_consts           ],
            "8": [None,             None,                   "Entered Data:"             ],
            "9": [None,             None,                   model_data.user_input_path             ],
        })
    else:
        logger.warning(
            f"Writing empty DataFrame."
            f"  Passed format was {format}"
            f"  And checked against {[f for f in FileExtensions]} which resulted in no match."
        )
        data = pd.DataFrame()

    return data


def get_valid_filename() -> str:
    """Helper function to create a valid, hopefully non duplicate, string to use as a file name.

    :return: Stringified time from ``datetime.now()`` in the form of %Y-%m-%d-result-from-%Hh%Mm.
    :rtype: str
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d-result-from-%Hh%Mm")


def write_file(
    data_frame: pd.DataFrame,
    file_format: FileExtensions = FileExtensions.EXCEL,
    destination: str = "./res/"
    ) -> None:
    """Writes the provided ``pd.DataFrame`` as either .xlsx or .csv
    to the hard-coded program's ``/res/`` directory.

    If there is no ``./res/`` directory relative to where the program was started from,
    that directory will be created.

    :param data_frame: The data frame that is to be written.
    :type data_frame: pd.DataFrame
    :param file_format: What format the written file should have, defaults to FileExtensions.EXCEL.
    :type file_format: FileExtensions, optional
    :raises TypeError: If the provided ``file_format`` was neither Excel nor CSV.
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
