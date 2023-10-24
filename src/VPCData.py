from collections import UserList

class VPCData(UserList):
    """
    A class to handle virtual patient data.
    Basically just a list atm.

    Args:
        UserList (class): wrapper around list objects
        
    ...
    
    Attributes
    ----------
    
    data: vec
        patient data
    
    
    Methods
    -------
    __getitem__(idx):
        returns the element of a given index in the data vector
        
    __setitem__(idx, value):
        sets a given value at a given index in the data vector
    
    __len__():
        return the lenght of the data vector
        
    __delitem__(idx):
        deletes data at a given index
        
    append(next):
        appends a given list or value to the data vector
        
    insert(idx, value):
        inserts a given list or value at the desired index in the data vector
        
    remove(value):
        deletes the given value from the data vector
        
    index(item, \*args):
        returns the index of a given item
    """

    def __init__(self, data=None):
        super().__init__(data)
        
    def __getitem__(self, idx):
        """
        returns the element of a given index in the data vector

        Args:
            idx (int): index in the data vector of the object

        Returns:
            data[idx]: data at a given index
        """
        if isinstance(idx, slice):
            return self.__class__(self.data[idx])
        else:
            return self.data[idx]
        
    def __setitem__(self, idx, value):
        """
        sets a given value at a given index in the data vector

        Args:
            idx (int): index in the data vector of the object
            value (any): value that should be at the given index
        """
        self.data[idx] = value
        
    def __len__(self):
        """
        return the lenght of the data vector

        Returns:
            int: objects lenght
        """
        return len(self.data)
    
    def __delitem__(self, idx):
        """
        deletes data at a given index

        Args:
            idx (int): index in the data vector of the object
        """
        del self.data[idx]
        
    def append(self, next):
        """
        appends a given list or value to the data vector

        Args:
            next (vec, float): input list or value to be appended
            to the objects data
        """
        if isinstance(next, list):
            for value in next:
                self.data.append(value)
        else:
            self.data.append(next)
        
    def insert(self, idx, value):
        """
        inserts a given list or value at the desired index in the data vector

        Args:
            idx (idx): index in the data vector of the object
            value (vec, float): given list or value to be inserted
        """
        if isinstance(value, list):
            for i, val in enumerate(value):
                self.data.insert(idx + i, val)
        else:
            self.data.insert(idx, value)
        
    def remove(self, value):
        """
        deletes the given value from the data vector

        Args:
            value (float): value in the data vector to be deleted

        Raises:
            ValueError: given value has to be in the objects data vector
        """
        if value not in self.data:
            raise ValueError("value not in list")
        self.data.remove(value)
        
    def index(self, item, *args):
        """
        returns the index of a given item
        
        Args:
            item (float): element of the objects data vector

        Raises:
            ValueError: input item has to be in the objects data vector

        Returns:
            int: index of the given item
        """
        if item not in self.data:
            raise ValueError("item not in list")
        return self.data.index(item, *args)