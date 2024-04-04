
# Standard library imports
import logging
from dataclasses import dataclass, field

# related third party imports
import pandas as pd

# Local imports
from src.FileHandler import FileExtensions


logger = logging.getLogger("ModelData")


@dataclass
class ModelData:
    """Container class that stores information for writing into the results file.

    :param fitted_model: The fitted model as a string.
    :type fitted_model: str | None
    :param fitted_consts: Dictionary of constants with keys of type `str` and values of type `float`.\
    Alternatively, a string containing the same information. Defaults to None.
    :type fitted_consts: dict[str, float] | str | None
    :param model: The model the program worked with. Defaults to "f(t) = ...".
    :type model: str, optional
    :param user_input_model: The exact model the user entered. Defaults to "f(t) = ...".
    :type user_input_model: str, optional
    :param parameter: The independent variable the program worked with. Defaults to ["..."].
    :type parameter: list[str], optional
    :param user_input_parameter: The exact independent variables the user entered. Defaults to "...".
    :type user_input_parameter: str, optional
    :param consts: The constants the program worked with. Defaults to ["..."].
    :type consts: list[str], optional
    :param user_input_consts: The exact constants the user entered. Defaults to ["..."].
    :type user_input_consts: list[str], optional
    :param user_input_path: The path to the data the user provided. Defaults to "path/to/data".
    :type user_input_path: str, optional
    """
    fitted_model: str | None = None
    fitted_consts: dict[str, float] | str | None = None
    model: str = "f(t) = ..."
    user_input_model: str = "f(t) = ..."
    parameter: list[str] = field(default_factory=lambda: ["..."])
    user_input_parameter: str = "..."
    consts: list[str] = field(default_factory=lambda: ["..."])
    user_input_consts: list[str] = field(default_factory=lambda: ["..."])
    user_input_path: str = "path/to/data"

    def create_dataframe_for(
        self,
        format: FileExtensions = FileExtensions.EXCEL
    ) -> pd.DataFrame:
        """Create a `pd.DataFrame` for the specified format, i.e. either Excel or CSV.
        The DataFrame contains information about the user inputs into the program and what the program
        made of those. It also contains the fit of the model if possible. If no fitted model string was
        given, a warning will be logged and the field in the DataFrame will read 'N/A'.

        :param format: The format for which the DataFrame is constructed. Defaults to FileExtensions.EXCEL.
        :type format: FileExtensions, optional
        :return: A DataFrame containing all input and output information.
        :rtype: pd.DataFrame
        """
        if self.fitted_model is None:
            logger.warning(f"Did not get a fitted model string.")
            self.fitted_model = "N/A"
            self.fitted_consts = "N/A"

        if format == FileExtensions.EXCEL:
            logger.debug(f"Creating DataFrame for {format} file")
            data = pd.DataFrame(
                index=range(1, 9),
                columns=["A", "B", "C", "D", "E"]
            )

            data.at[1,"A"]  = "Fitted Model:"
            data.at[1,"B"]  = self.fitted_model
            data.at[2,"A"]  = "Fitted Constants:"
            data.at[2,"B"]  = self.fitted_consts
            data.at[4,"A"]  = "Interpreted Data"
            data.at[4,"D"]  = "Raw Data"
            data.at[5,"A"]  = "Model:"
            data.at[5,"B"]  = self.model
            data.at[5,"D"]  = "Entered Model:"
            data.at[5,"E"]  = self.user_input_model
            data.at[6,"A"]  = "Independent Var:"
            data.at[6,"B"]  = self.parameter
            data.at[6,"D"]  = "Entered Independent Var:"
            data.at[6,"E"]  = self.user_input_parameter
            data.at[7,"A"] = "Constants:"
            data.at[7,"B"] = self.consts
            data.at[7,"D"] = "Entered Constants:"
            data.at[7,"E"] = self.user_input_consts
            data.at[8,"D"] = "Entered Data:"
            data.at[8,"E"] = self.user_input_path

        elif format == FileExtensions.CSV:
            logger.debug("Creating DataFrame for {format} file")
            data = pd.DataFrame({
                "1": ["Fitted Model:",  "Interpreted",          "Raw"                       ],
                "2": [self.fitted_model,"Model:",               "Entered Model:"            ],
                "3": [None,             self.model,             self.user_input_model       ],
                "4": [None,             "Independent Var:",     "Entered Independent Var:"  ],
                "5": [None,             self.parameter,         self.user_input_parameter   ],
                "6": [None,             "Constants:",           "Entered Constants:"        ],
                "7": [None,             self.consts,            self.user_input_consts      ],
                "8": [None,             None,                   "Entered Data:"             ],
                "9": [None,             None,                   self.user_input_path        ],
            })
        else:
            logger.warning(
                f"Writing empty DataFrame."
                f"  Passed format was {format}"
                f"  And checked against {[f for f in FileExtensions]} which resulted in no match."
            )
            data = pd.DataFrame()

        return data