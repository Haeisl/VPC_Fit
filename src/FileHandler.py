import pandas as pd
from pathlib import Path

i = 0

def read_file(file_path: str) -> pd.DataFrame:
    if not Path(file_path).is_file():
        raise FileNotFoundError("Invalid Path; no file at destination")
    
    suffix = Path(file_path).suffix.split('.')[1]
    if suffix == '':
        raise ValueError("No Fileextension found at path")
    
    if suffix.upper() == 'XLSX':
        data_frame = pd.read_excel(file_path)
    elif suffix.upper() == 'CSV':
        data_frame = pd.read_csv(file_path)
    elif suffix.upper() == 'XML':
        data_frame = pd.read_xml(file_path)
    else:
        raise TypeError("Unknown File extension")

    return data_frame


def format_data(data_frame: pd.DataFrame, include_first_row: bool) -> list[list]:
    if data_frame is None:
        raise ValueError("No data could be read") 
    
    column_names = data_frame.columns.tolist()
    data_list = []

    if include_first_row:
        data_list = [list([name, *data_frame[name].tolist()]) for name in column_names]
    else:
        data_list = [list(data_frame[name].tolist()) for name in column_names]

    return data_list


def write_file(data_frame: pd.DataFrame, file_format, data) -> None: 
    resPath = './results/res_' + str(i)
    data_frame = pd.data_frame(data)
    if file_format == 'EXCEL':
        data_frame.to_excel(resPath + '.xlsx', index=False)
    elif file_format == 'XML':
        data_frame.to_xml(resPath + '.xml', index=False)
    elif file_format == 'CSV':
        data_frame.to_csv(resPath + '.csv', index=False)
    else:
        raise TypeError("Can't write to unknown file extension")
    i += 1


def validate_data():
    pass