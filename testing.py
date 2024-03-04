from enum import Enum
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
                pa.Check(lambda series: series.apply(lambda x: isinstance(x, (int, float))), name="check 1"),
                pa.Check(lambda series: len(series) != 0, name="check 2")
            ],
            nullable=False
        ) for col in df.columns
    }, coerce=True)

    return schema.validate(df)

def main() -> None:
    # data = {
    #     "col1": [1.0, 2.0, 3.0],
    #     "col2": [4, 5, 6],
    #     "col3": [7.0, 8.0, 9.0],
    #     "col4": [4, 5, 6],
    #     "col5": [7.0, 8.0, 9.0],
    #     "col6": [4, 5, 6],
    #     "col8": [],
    # }
    # df = pd.DataFrame()
    # cdf = Schema.validate(df)
    # # cdf = check_file(df)
    # print(cdf)
    print([f.name for f in Colors])

if __name__ == '__main__':
    main()