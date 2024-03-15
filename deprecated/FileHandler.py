import pandas as pd
from pathlib import Path

class FileHandler():
    i = 0

    FORMATS = ['EXCEL', 'CSV', 'XML']

    def __init__(self, path=None, file_name="file_" + str(i), format=None, patient_data=None):
        """Constructor method

        :param path: path to the file to be read or written, defaults to None
        :type path: str, optional
        :param file_name: name of the file to be written, defaults to file_+str(i)
        :type file_name: str, optional
        :param format: format of the file to be written, defaults to None
        :type format: str, optional
        :param patient_data: data to be read from or written to the file, defaults to None
        :type patient_data: any, optional
        """
        self.path = path
        self.file_name = file_name
        self.format = format
        self.patient_data = patient_data


    def read_file(self):
        """reads data from a file and returns a data_frame

        :raises FileNotFoundError: objects path has to be valid
        :raises ValueError: file of the specified path must have a format
        :raises TypeError: objects format is unknown, data can't be read
        :return: the data read from the file
        :rtype: data_frame
        """

        if not Path(self.path).is_file():
            raise FileNotFoundError("Invalid Path; no file at destination")

        suffix = Path(self.path).suffix.split('.')[1]
        if suffix == '':
            raise ValueError("No Fileextension found at path")

        if suffix.upper() == 'XLSX':
            self.data_frame = pd.read_excel(self.path)
        elif suffix.upper() == 'CSV':
            self.data_frame = pd.read_csv(self.path)
        elif suffix.upper() == 'XML':
            self.data_frame = pd.read_xml(self.path)
        else:
            raise TypeError("Unknown File extension")

        return self.data_frame


    def format_data(self, include_first_row:bool):
        """formats read data from a file to a list and transforms it to a VPCData object

        :param include_first_row: -deprecated-
        :type include_first_row: bool
        :raises ValueError: object has to be in read mode
        :return: the transformed read data
        :rtype: list[list]
        """

        # return self.data_frame.values.tolist() if self.data_frame is not None else []

        if self.data_frame is None:
            raise ValueError("No data could be read")

        column_names = self.data_frame.columns.tolist()
        vpc_data_list = []

        if include_first_row:
            vpc_data_list = [list([name, *self.data_frame[name].tolist()]) for name in column_names]
        else:
            vpc_data_list = [list(self.data_frame[name].tolist()) for name in column_names]

        return vpc_data_list # , self.data_frame


    def write_file(self, data):
        """writes the given data into a file

        :param data: data to be written to a file
        :type data: any
        :raises TypeError: file format of the file to be written can only be one of the supported ones (excel, csv, xml)
        """

        resPath = './results/res_' + str(FileHandler.i)
        self.data_frame = pd.data_frame(data)
        if self.file_format == 'EXCEL':
            self.data_frame.to_excel(resPath + '.xlsx', index=False)
        elif self.file_format == 'XML':
            self.data_frame.to_xml(resPath + '.xml', index=False)
        elif self.file_format == 'CSV':
            self.data_frame.to_csv(resPath + '.csv', index=False)
        else:
            raise TypeError("Can't write to unknown file extension")
        FileHandler.i += 1


    def validate_data(self):
        """TODO
        read data_frame / patient_data and discard rows, if they are not fully populated
        think of way other than discarding incomplete data
        """
        pass