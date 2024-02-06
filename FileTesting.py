import pandas as pd
from pathlib import Path
from datetime import datetime
import os

def read_file(file_path: str) -> pd.DataFrame:
    if not Path(file_path).is_file():
        raise FileNotFoundError('Invalid Path; no file at destination')

    suffix = Path(file_path).suffix.split('.')[1]
    if suffix == '':
        raise ValueError('No Fileextension found at path')

    if suffix.upper() == 'XLSX':
        data_frame = pd.read_excel(file_path)
    elif suffix.upper() == 'CSV':
        data_frame = pd.read_csv(file_path)
    else:
        raise TypeError('Unknown File extension')

    return data_frame


def dataframe_tolist(data_frame: pd.DataFrame, include_first_row: bool) -> list[list]:
    if data_frame is None:
        raise ValueError('No data could be read')

    column_names = data_frame.columns.tolist()

    if include_first_row:
        data_list = [[name, *data_frame[name].tolist()] for name in column_names]
    else:
        data_list = [data_frame[name].tolist() for name in column_names]

    return data_list


def create_dataframe_from_for(
    fitted_model: str = 'f(t) = ...',
    model: str = 'f(t) = ...',
    user_input_model: str = 'f(t) = ...',
    parameter: str = '...',
    user_input_parameter: str = '...',
    consts: str = '...',
    user_input_consts: str = '...',
    user_input_path: str = 'path/to/data',
    format: str = 'Excel'
) -> pd.DataFrame:

    if format == 'Excel':
        data = pd.DataFrame(
            index=range(1, 13),
            columns=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        )

        data.at[1,'A'] = 'Fitted Model'
        data.at[1,'C'] = fitted_model
        data.at[4,'A'] = 'Interpreted Data'
        data.at[4,'G'] = 'Raw Data'
        data.at[6,'A'] = 'Model'
        data.at[6,'C'] = model
        data.at[6,'G'] = 'Entered Model'
        data.at[6,'I'] = user_input_model
        data.at[8,'A'] = 'Parameter'
        data.at[8,'C'] = parameter
        data.at[8,'G'] = 'Entered Parameter'
        data.at[8,'I'] = user_input_parameter
        data.at[10,'A'] = 'Constants'
        data.at[10,'C'] = consts
        data.at[10,'G'] = 'Entered Constants'
        data.at[10,'I'] = user_input_consts
        data.at[12,'G'] = 'Entered Data'
        data.at[12,'I'] = user_input_path

    elif format == 'CSV':
        data = pd.DataFrame({
            '1': ['Fitted Model:',  'Interpreted:',     'Raw:'],
            '2': [fitted_model,     'Model:',           'Entered Model:'],
            '3': [None,             model,              user_input_model],
            '4': [None,             'Parameter:',       'Entered Parameter:'],
            '5': [None,             parameter,          user_input_parameter],
            '6': [None,             'Constants:',       'Entered Constants:'],
            '7': [None,             consts,             user_input_consts],
            '8': [None,             None,               'Entered Data:'],
            '9': [None,             None,               user_input_path],
        })

    return data


def get_valid_filename() -> str:
    now = datetime.now()
    return now.strftime("%Y-%m-%d-result-from-%Hh%Mm%Ss")


def write_file(data_frame: pd.DataFrame, file_format: str = 'EXCEL') -> None:
    relative_path = './res/'
    if not os.path.exists(relative_path):
        os.makedirs(relative_path)
    file_name = get_valid_filename()
    if file_format == 'EXCEL':
        file_name = file_name + '.xlsx'
        data_frame.to_excel(os.path.join(relative_path, file_name), index=False, header=False)
    elif file_format == 'CSV':
        file_name = file_name + '.csv'
        data_frame.to_csv(os.path.join(relative_path, file_name), index=False, header=False, sep='\t')
    else:
        raise TypeError('Can\'t write to unknown file extension')


def is_file_empty(file_path):
    return os.stat(file_path).st_size == 0


def main():
    path = input("path: ")

    # data = read_file(path)

    # fdata = format_data(data, True)
    # data = create_dataframe_from_for(format='CSV')
    # write_file(data, file_format='CSV')

    print(is_file_empty(path))


if __name__ == '__main__':
    main()