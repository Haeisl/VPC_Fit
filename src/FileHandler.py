from src.VPCData import VPCData
import pandas as pd
from pathlib import Path
# import xml.etree.ElementTree as ET

class FileHandler():
    """This is a class to handle files

    :raises ValueError: _description_
    :raises ValueError: _description_
    :raises ValueError: _description_
    :raises ValueError: _description_
    :raises ValueError: _description_
    :raises ValueError: _description_
    :raises ValueError: _description_
    :raises FileNotFoundError: _description_
    :raises ValueError: _description_
    :raises TypeError: _description_
    :raises ValueError: _description_
    :raises ValueError: _description_
    :raises TypeError: _description_
    :return: _description_
    :rtype: _type_
    """
    
    i = 0
    
    FORMATS = ['EXCEL', 'CSV', 'XML']
    
    MODES = ['READ', 'WRITE']
    
    def __init__(self, path=None, mode=None, fileName="file_" + str(i), format=None, patientData=None):
        """Constructor method

        :param path: path to the file to be read or written, defaults to None
        :type path: str, optional
        :param mode: mode of the object which can be either read or write, defaults to None
        :type mode: str, optional
        :param fileName: name of the file to be written, defaults to file_+str(i)
        :type fileName: str, optional
        :param format: format of the file to be written, defaults to None
        :type format: str, optional
        :param patientData: data to be read from or written to the file, defaults to None
        :type patientData: any, optional
        """
        self.path = path
        self.mode = mode
        self.fileName = fileName
        self.format = format
        self.patientData = patientData

    @classmethod
    def ReadMode(cls, path):
        """classmethod, returns a FileHandler class obejct in read mode

        :param path: path to the file to be read
        :type path: str
        :return: class object in read mode with the path to the respective file
        :rtype: FileHandler
        """
        return cls(path=path, mode='r')
    
    @classmethod
    def WriteMode(cls, path, fileName, format, pData):
        """classmethod, returns a FileHandler class object in write mode

        :param path: path to the file to be written
        :type path: str
        :param fileName: name of the file to be written
        :type fileName: str
        :param format: format of the file to be written
        :type format: str
        :param pData: data to be written
        :type pData: any
        :return: class object in write mode with the path, fileName, format and patient data for the respective file to be written
        :rtype: FileHandler
        """
        return cls(path=path, mode='w', fileName=fileName, format=format, patientData=pData)
    
    @property
    def mode(self):
        """gets the mode of the object

        :return: current mode of the object
        :rtype: str
        """
        return self._mode
    
    @mode.setter
    def mode(self, mode):
        """sets the mode of the object to the given value

        :param mode: mode of the object
        :type mode: str
        :raises ValueError: input value can only be a string of 'read' or 'write'
        """
        if mode.upper() in self.MODES:
            self._mode = mode.upper()
        elif mode == 'r':
            self._mode = 'READ'
        elif mode == 'w':
            self._mode = 'WRITE'
        else:
            raise ValueError("Unknown mode, specify 'read' or 'write'")
    
    @property
    def path(self):
        """gets the path of the file to be read or write

        :return: current path of the object
        :rtype: str
        """
        return self._path
    
    @path.setter
    def path(self, path):
        """sets the path of the file that is being read or written to

        :param path: path of the object
        :type path: str
        :raises ValueError: path has to be a string
        :raises ValueError: illegal characters are not allowed to be in a path
        """
        if not isinstance(path, str):
            raise ValueError("Path must be of type string")
        if any(c in path for c in '<>"|?*'):
            raise ValueError("Illegal character in path")
        self._path = path
        
    @property
    def fileName(self):
        """gets the name of the file to be written

        :return: current fileName of the object
        :rtype: str
        """
        return self._fileName
    
    @fileName.setter
    def fileName(self, name):
        """sets the name of the file to be written to the input value

        :param name: file name of the object
        :type name: str
        :raises ValueError: input has to be a string
        :raises ValueError: input must not contain dots or commas
        """
        if not isinstance(name, str):
            raise ValueError("File name needs to be a string")
        if any(c in name for c in ',.'):
            raise ValueError("File name can't contain dots, commas, etc.")
        self._fileName = name
                
    @property
    def fileFormat(self):
        """gets the format of the file

        :return: current file format of the object
        :rtype: str
        """
        return self._fileFormat 
    
    @fileFormat.setter
    def fileFormat(self, fileFormat):
        """sets the format of the file to the input value

        :param fileFormat: file format of the object
        :type fileFormat: str
        :raises ValueError: input file format has to be in the pre-defined dict otherwise the given format is not supported
        """
        if fileFormat not in self.FORMATS:
            raise ValueError("Unknown file format")
        self._fileFormat = fileFormat
    
    def readFile(self):
        """reads data from a file and returns a dataframe

        :raises ValueError: object has so be in read mode
        :raises FileNotFoundError: objects path has to be valid
        :raises ValueError: file of the specified path must have a format
        :raises TypeError: objects format is unknown, data can't be read
        :return: the data read from the file
        :rtype: dataframe
        """
        if not self.mode == 'READ':
            raise ValueError("FileHandler not in read mode")
        if not Path(self.path).is_file():
            raise FileNotFoundError("Invalid Path; no file at destination")
            
        suffix = Path(self.path).suffix.split('.')[1]
        if suffix == '':
            raise ValueError("No Fileextension found at path")
        
        if suffix.upper() == 'XLSX':
            self.dataFrame = pd.read_excel(self.path)
        elif suffix.upper() == 'CSV':
            self.dataFrame = pd.read_csv(self.path)
        elif suffix.upper() == 'XML':
            self.dataFrame = pd.read_xml(self.path)
        else:
            raise TypeError("Unknown File extension")
        
        return self.dataFrame
                
    def formatData(self, includeFirstRow:bool):
        """formats read data from a file to a list and transforms it to a VPCData object

        :param includeFirstRow: -deprecated-
        :type includeFirstRow: bool
        :raises ValueError: object has to be in read mode
        :return: the transformed read data
        :rtype: list[VPCData]
        """
        # if self.mode != 'READ':
        #    raise ValueError("Can't read file while not in read mode")
        # return self.dataFrame.values.tolist() if self.dataFrame is not None else []
        
        if self.dataFrame is None:
            raise ValueError("No data could be read")
        
        columnNames = self.dataFrame.columns.tolist()
        vpcDataList = []
        
        if includeFirstRow:
            vpcDataList = [VPCData([name, *self.dataFrame[name].tolist()]) for name in columnNames]
        else:
            vpcDataList = [VPCData(self.dataFrame[name].tolist()) for name in columnNames]
        
        return vpcDataList # , self.dataFrame

    
    def writeFile(self, data):
        """writes the given data into a file

        :param data: data to be written to a file
        :type data: any
        :raises ValueError: object has to be in write mode
        :raises TypeError: file format of the file to be written can only be one of the supported ones (excel, csv, xml)
        """
        if self.mode != 'write':
            raise ValueError("Can't write while not in write mode")
        
        resPath = './results/res_' + str(FileHandler.i) 
        self.dataFrame = pd.DataFrame(data)
        if self.fileFormat == 'EXCEL':
            self.dataFrame.to_excel(resPath + '.xlsx', index=False)
        elif self.fileFormat == 'XML':
            self.dataFrame.to_xml(resPath + '.xml', index=False)
        elif self.fileFormat == 'CSV':
            self.dataFrame.to_csv(resPath + '.csv', index=False)
        else:
            raise TypeError("Can't write to unknown Fileextension")
        FileHandler.i += 1
        
    def validateData(self):
        """TODO
        read dataFrame / patientData and discard rows, if they are not fully populated
        think of way other than discarding incomplete data
        """
        pass