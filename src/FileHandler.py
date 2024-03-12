# standard library imports
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Union

# related third party imports
import pandas as pd


logger = logging.getLogger("FileHandler")

class FileExtensions(Enum):
    EXCEL = "XLSX"
    CSV = "CSV"


def is_extension_supported(file_path: str) -> bool:
    suffix = Path(file_path).suffix.split(".")[1]
    return suffix.upper() in [extension.value for extension in FileExtensions]


def read_file(file_path: str) -> pd.DataFrame:
    if not Path(file_path).is_file():
        raise FileNotFoundError("Invalid Path; no file at destination")

    suffix = Path(file_path).suffix.split(".")[1]
    if suffix == "":
        raise ValueError("No file extension found at path")

    if suffix.upper() == FileExtensions.EXCEL.value:
        data_frame = pd.read_excel(file_path)
    elif suffix.upper() == FileExtensions.CSV.value:
        data_frame = pd.read_csv(file_path)
    else:
        raise TypeError("Invalid file extension")

    return data_frame


def dataframe_tolist(data_frame: pd.DataFrame) -> list[list[Union[float, int]]]:
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
    fitted_model: Optional[str],
    fitted_consts: Optional[Union[dict[str, float], str]],
    model: str = "f(t) = ...",
    user_input_model: str = "f(t) = ...",
    parameter: list[str] = ["..."],
    user_input_parameter: str = "...",
    consts: list[str] = ["..."],
    user_input_consts: list[str] = ["..."],
    user_input_path: str = "path/to/data",
    format: FileExtensions = FileExtensions.EXCEL
) -> pd.DataFrame:

    if fitted_model is None:
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
        data.at[5,"B"]  = model
        data.at[5,"D"]  = "Entered Model:"
        data.at[5,"E"]  = user_input_model
        data.at[6,"A"]  = "Independent Var:"
        data.at[6,"B"]  = parameter
        data.at[6,"D"]  = "Entered Independent Var:"
        data.at[6,"E"]  = user_input_parameter
        data.at[7,"A"] = "Constants:"
        data.at[7,"B"] = consts
        data.at[7,"D"] = "Entered Constants:"
        data.at[7,"E"] = user_input_consts
        data.at[8,"D"] = "Entered Data:"
        data.at[8,"E"] = user_input_path

    elif format == FileExtensions.CSV:
        data = pd.DataFrame({
            "1": ["Fitted Model:",  "Interpreted",          "Raw"                       ],
            "2": [fitted_model,     "Model:",               "Entered Model:"            ],
            "3": [None,             model,                  user_input_model            ],
            "4": [None,             "Independent Var:",     "Entered Independent Var:"  ],
            "5": [None,             parameter,              user_input_parameter        ],
            "6": [None,             "Constants:",           "Entered Constants:"        ],
            "7": [None,             consts,                 user_input_consts           ],
            "8": [None,             None,                   "Entered Data:"             ],
            "9": [None,             None,                   user_input_path             ],
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
    now = datetime.now()
    return now.strftime("%Y-%m-%d-result-from-%Hh%Mm")


def write_file(data_frame: pd.DataFrame, file_format: FileExtensions = FileExtensions.EXCEL) -> None:
    relative_path = Path("./res/")

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
        raise TypeError("Can\"t write to unknown file extension")
