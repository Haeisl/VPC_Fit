from collections import UserList

class VPCData(UserList):
    """This is a class to handle virtual patient data. Basically just a list atm.

    :param UserList: wrapper around list objects
    :type UserList: class
    """

    def __init__(self, data=None):
        """Constructor method

        :param data: patient data read from the input files or generated virtual patient data, defaults to None
        :type data: list, optional
        """
        super().__init__(data)
        
    def __getitem__(self, idx):
        """returns the element of a given index in the data list

        :param idx: index in the data list of the object
        :type idx: int
        :return: data at a given index
        :rtype: float
        """
        if isinstance(idx, slice):
            return self.__class__(self.data[idx])
        else:
            return self.data[idx]
        
    def __setitem__(self, idx, value):
        """sets a given value at a given index in the data list

        :param idx: index in the data list of the object
        :type idx: int
        :param value: value that should be at the given index
        :type value: float
        """
        self.data[idx] = value
        
    def __len__(self):
        """returns the length of the data list

        :return: objects length
        :rtype: int
        """
        return len(self.data)
    
    def __delitem__(self, idx):
        """deletes an element in the data list at a given index

        :param idx: index in the data list
        :type idx: int
        """
        del self.data[idx]
        
    def append(self, next):
        """appends a given list or value to the data list

        :param next: input list or value to be appended to the objects data
        :type next: any
        """
        if isinstance(next, list):
            for value in next:
                self.data.append(value)
        else:
            self.data.append(next)
        
    def insert(self, idx, value):
        """inserts a given list or value at the desired index in the data list

        :param idx: index in the data list of the object
        :type idx: int
        :param value: given list or value to be inserted
        :type value: any
        """
        if isinstance(value, list):
            for i, val in enumerate(value):
                self.data.insert(idx + i, val)
        else:
            self.data.insert(idx, value)
        
    def remove(self, value):
        """deletes the given value from the data list

        :param value: value in the data list to be deleted
        :type value: float
        :raises ValueError: given value has to be in the objects data list
        """
        if value not in self.data:
            raise ValueError("value not in list")
        self.data.remove(value)
        
    def index(self, item, *args):
        """returns the index of a given element in the data list

        :param item: element of the objects data list
        :type item: float
        :raises ValueError: input element has to be in the objects data list
        :return: index of the given element
        :rtype: int
        """
        if item not in self.data:
            raise ValueError("item not in list")
        return self.data.index(item, *args)