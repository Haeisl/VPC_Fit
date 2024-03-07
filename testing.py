from enum import Enum
from typing import Union
import pandas as pd
import pandera as pa
from pandera.typing import Index, DataFrame, Series

class Colors(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "Blue"

class Schema(pa.SchemaModel):
    column1: Series[int]

def check_file(df: pd.DataFrame) -> pd.DataFrame:
    schema = pa.DataFrameSchema({
        col: pa.Column(
            checks=[
                pa.Check(lambda series: series.apply(lambda x: isinstance(x, (int, float))), name="check 1")
            ],
            nullable=False
        ) for col in df.columns
    }, coerce=True)

    return schema.validate(df)

def dataframe_tolist(
    data_frame: pd.DataFrame, include_first_row: bool
) -> list[list[Union[str, float, int]]]:
    if data_frame is None:
        raise ValueError("No data could be read")

    if data_frame.empty:
        raise ValueError("DataFrame is empty")

    column_names = data_frame.columns.tolist()

    if include_first_row:
        data_list = [[name, *data_frame[name].tolist()] for name in column_names]
    else:
        data_list = [data_frame[name].tolist() for name in column_names]

    return data_list

def main() -> None:
    data = {
        "col1": [1.0, 2.0, 3.0],
        "col2": [4, 5, 6],
        "col3": [7.0, 8.0, 9.0],
        "col4": [4, 5, 6],
        "col5": [7.0, 8.0, 9.0],
        "col6": [4, 5, 6],
        "col8": [None,2,3],
    }
    df = pd.DataFrame(data)

    l = dataframe_tolist(df, True)
    print(l)

if __name__ == '__main__':
    main()