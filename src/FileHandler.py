from VPCData import VPCData
import pandas as pd
from pathlib import Path
# import xml.etree.ElementTree as ET

class FileHandler():
    """
    A class to handle files

    ...
    
    Attributes
    ----------
    
    path: str
        path to the file to be read or written
    mode: str
        mode of the object, either read or write
    fileName: str
        name of the file to be written
    format: str
        format of the file to be written
    patientData: any
        data to be read from or written to the file
        
    
    Methods
    -------
    ReadMode():
        returns a class obejct in read mode
        
    WriteMode():
        returns a class object in write mode
        
    mode():
        returns the mode of the object
        
    mode(value):
        sets the mode of the object
        
    path():
        returns the path of the object
        
    path(value):
        sets the path of the object
        
    fileName():
        returns the name of the file to be written
        
    fileName(value):
        sets the name of the file to be written
        
    fileformat():
        return the format of the file
        
    fileformat(value):
        sets the format of the file
        
    readFile():
        reads data from a file and returns a dataframe
        
    formatData():
        the read data stored as dataFrame is formatted to a list
        
    writeFile(data):
        writes the input data into a file
        
    validateData():
        TODO

    """
    
    i = 0
    
    FORMATS = ['EXCEL', 'CSV', 'XML']
    
    MODES = ['READ', 'WRITE']
    
    def __init__(self, path=None, mode=None, fileName="file_" + str(i), format=None, patientData=None):
        self.path = path
        self.mode = mode
        self.fileName = fileName
        self.format = format
        self.patientData = patientData

    @classmethod
    def ReadMode(cls, path):
        """
        classmethod

        Args:
            path (str): path to the file to be read

        Returns:
            FileHandler: class object in read mode 
            with the path to the respective file
        """
        return cls(path=path, mode='r')
    
    @classmethod
    def WriteMode(cls, path, fileName, format, pData):
        """
        classmethod

        Args:
            path (str): _description_
            fileName (str): _description_
            format (str): _description_
            pData (any): _description_

        Returns:
            FileHandler: class object in write mode
            with the path, fileName, format and patient data 
            for the respective file to be written
        """
        return cls(path=path, mode='w', fileName=fileName, format=format, patientData=pData)
    
    @property
    def mode(self):
        """
        gets the mode of the object

        Returns:
            mode (str): string of the object's mode
        """
        return self._mode
    
    @mode.setter
    def mode(self, mode):
        """
        sets the mode of the object

        Args:
            mode (str): string of the mode that will be set to the input

        Raises:
            ValueError: input value can only be a string of read or write
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
        """
        gets the path of the file to be read or write

        Returns:
            path (str): path of the object
        """
        return self._path
    
    @path.setter
    def path(self, path):
        """
        sets the path of the file to be read or write

        Args:
            path (str): path of the object

        Raises:
            ValueError: path has to be a string
            ValueError: illegal characters are not allowed to be in a path
        """
        if not isinstance(path, str):
            raise ValueError("Path must be of type string")
        if any(c in path for c in '<>"|?*'):
            raise ValueError("Illegal character in path")
        self._path = path
        
    @property
    def fileName(self):
        """
        gets the fileName of the file to be written

        Returns:
            fileName (str): fileName of the object
        """
        return self._fileName
    
    @fileName.setter
    def fileName(self, name):
        """
        sets the fileName of the file to be written

        Args:
            name (str): fileName of the object

        Raises:
            ValueError: input has to be a string
            ValueError: input must not contain dots or commas
        """
        if not isinstance(name, str):
            raise ValueError("File name needs to be a string")
        if any(c in name for c in ',.'):
            raise ValueError("File name can't contain dots, commas, etc.")
        self._fileName = name
                
    @property
    def fileFormat(self):
        """
        gets the format of the file

        Returns:
            fileFormat (str): file format of the object
        """
        return self._fileFormat 
    
    @fileFormat.setter
    def fileFormat(self, fileFormat):
        """
        set the file format

        Args:
            fileFormat (str): fileformat of the object

        Raises:
            ValueError: input file format has to be in the pre-defined dict
            otherwise the given format is not supported
        """
        if fileFormat not in self.FORMATS:
            raise ValueError("Unknown file format")
        self._fileFormat = fileFormat
    
    def readFile(self):
        """
        reads from a file and stores the data in it

        Raises:
            ValueError: object has so be in read mode
            FileNotFoundError: objects path has to be valid
            ValueError: file of the specified path must have a format
            TypeError: objects format is unknown, data can't be read
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
        """
        formats the read data to a list
        and transforms it to a VPCData object

        Raises:
            ValueError: object has to be in read mode

        Returns:
            dataFrame (float): the read data as a list
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
        """
        write a file with given data

        Args:
            data (_type_): input data to be written to a file

        Raises:
            ValueError: object has to be in write mode
            TypeError: file format of the file to be written 
            can only be one of the supported ones
            (Excel, xml, csv)
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
        """
        TODO
        read dataFrame / patientData and discard rows, if they are not fully populated
        think of way other than discarding incomplete data
        """
        pass