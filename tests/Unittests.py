import unittest

from src.VPCData import VPCData
from src.FileHandler import FileHandler

class TestVPCData(unittest.TestCase):
    """_summary_

    _extended_summary_

    :param unittest: _description_
    :type unittest: _type_
    """
    def setUp(self):
        print("Running setUp method...")
        self.data_1 = VPCData(["a", "b", "c", "d"])
        self.data_2 = VPCData([1.1, 2.2, 3.3, 4.4])
        self.data_3 = VPCData(["a", 2.2, "c", 4.4])
        
    def test_init(self):
        print("Running __init__ tests...")
        obj1 = VPCData()
        obj2 = VPCData([])
        obj3 = VPCData([1,2,3])
        self.assertEqual(obj1.data, [])
        self.assertEqual(obj2.data, [])
        self.assertEqual(obj3.data, [1,2,3])
        self.assertIsInstance(obj1, VPCData)
        self.assertIsInstance(obj2, VPCData)
        self.assertIsInstance(obj3, VPCData)
    
    def test_getItem(self):
        """_summary_

        _extended_summary_
        """
        print("Running __getitem__ tests...")
        self.assertEqual(self.data_1[0], "a")
        self.assertEqual(self.data_2[1], 2.2)
        self.assertEqual(self.data_3[2], "c")
        
        self.assertEqual(self.data_1[:2], ["a", "b"])
        self.assertEqual(self.data_2[1:3], [2.2, 3.3])
        self.assertEqual(self.data_3[2:], ["c", 4.4])
        
    def test_setItem(self):
        print("Running __setItem__ tests...")
        self.data_1[0] = 0.0
        self.assertEqual(self.data_1, [0.0, "b", "c", "d"])
        self.data_2[1] = "eins"
        self.assertEqual(self.data_2, [1.1, "eins", 3.3, 4.4])
        self.data_3[2] = 3
        self.assertEqual(self.data_3, ["a", 2.2, 3, 4.4])
        
    def test_len(self):
        print("Running __len__ tests...")
        obj4 = VPCData()
        self.assertEqual(len(self.data_1), 4)
        self.assertEqual(len(self.data_2), 4)
        self.assertEqual(len(self.data_3), 4)
        self.assertEqual(len(obj4), 0)
        
    def test_delitem(self):
        print("Running __delitem__ tests...")
        del self.data_1[1]
        self.assertEqual(self.data_1, ["a", "c", "d"])
        del self.data_1[0]
        self.assertEqual(self.data_1, ["c", "d"])
        del self.data_1[1]
        self.assertEqual(self.data_1, ["c"])
        del self.data_1[0]
        self.assertEqual(self.data_1, [])
        
    def test_append(self):
        print("Running append tests...")
        self.data_1.append("e")
        self.assertEqual(self.data_1, ["a", "b", "c", "d", "e"])
        self.data_2.append([5.5, 6.6])
        self.assertEqual(self.data_2, [1.1, 2.2, 3.3, 4.4, 5.5, 6.6])
        self.data_3.append([])
        self.assertEqual(self.data_3, ["a", 2.2, "c", 4.4])
        
    def test_insert(self):
        print("Running insert tests...")
        self.data_1.insert(0, "z")
        self.assertEqual(self.data_1, ["z", "a", "b", "c", "d"])
        self.data_2.insert(2, [2.3, 2.4, 2.5])
        self.assertEqual(self.data_2, [1.1, 2.2, 2.3, 2.4, 2.5, 3.3, 4.4])
        self.data_2.insert(-1, 3.6)
        self.assertEqual(self.data_2, [1.1, 2.2, 2.3, 2.4, 2.5, 3.3, 3.6, 4.4])
        self.data_3.insert(0, [])
        self.assertEqual(self.data_3, ["a", 2.2, "c", 4.4])
        
    def test_remove(self):
        print("Running remove tests...")
        self.data_1.remove("a")
        self.assertEqual(self.data_1, ["b", "c", "d"])
        with self.assertRaises(ValueError):
            self.data_2.remove(5.5)
        
    def test_index(self):
        print("Running index tests...")
        self.assertEqual(self.data_2.index(1.1), 0)
        with self.assertRaises(ValueError):
            self.data_1.index(5)
        with self.assertRaises(ValueError):
            self.data_2.index([2.2, 3.3]) 
    
class TestFileHandler(unittest.TestCase):
    """_summary_

    _extended_summary_

    :param unittest: _description_
    :type unittest: _type_
    """
    
    def setUp(self):
        print("Running setUp method...")
        self.handler_r = FileHandler.Read(".")
        self.handler_w = FileHandler.Write(".", "filey", "xml", [1,2,3])
        
    def test_init(self):
        """_summary_

        _extended_summary_
        """
        print("Running __init__ tests...")
        with self.assertRaises(Exception):
            handler_blank0 = FileHandler()
        with self.assertRaises(Exception):
            handler_blank1 = FileHandler('.')
    
    def test_getsetMode(self):
        print("Running setMode and getMode tests...")
        r = 'READ'
        w = 'WRITE'
        self.assertEqual(self.handler_r.mode, r)
        self.assertEqual(self.handler_w.mode, w)
        with self.assertRaises(Exception):
            self.handler_r.mode = None
        self.handler_r.mode = 'rEaD'
        self.assertEqual(self.handler_r.mode, 'READ')
        self.handler_w.mode = 'write'
        self.assertEqual(self.handler_w.mode, 'WRITE')
        with self.assertRaises(Exception):
             self.handler_r.mode = 1
        with self.assertRaises(Exception):
             self.handler_r.mode = 'ead'
        with self.assertRaises(Exception):
             self.handler_r.mode = 'rite'

    def test_getsetPath(self):
        print("Running getPath and setPath tests...")
        with self.assertRaises(ValueError):
            self.handler_r.path = "./<filename>"
        self.handler_w.path = "./classes"
        self.assertEqual(self.handler_w.path, "./classes")
        with self.assertRaises(ValueError):
            self.handler_w.path = None
        with self.assertRaises(ValueError):
            self.handler_r.path = 123
        
    def test_getsetFilename(self):
        print("Running getFilename and setFilename tests...")
        with self.assertRaises(ValueError):
            self.handler_r.filename = 123
        with self.assertRaises(ValueError):
            self.handler_w.filename = "file.name"
        self.handler_w.filename = "file1"
        self.assertEqual(self.handler_w.filename, "file1")
        with self.assertRaises(ValueError):
            self.handler_r.filename = None
    
    def test_getsetFileFormat(self):
        print("Running getFileFormat and setFileFormat tests...")
        with self.assertRaises(ValueError):
            self.handler_r.fileFormat = "PDF"
        self.handler_w.fileFormat = 'XML'
        self.assertEqual(self.handler_w.fileFormat, 'XML')
        with self.assertRaises(ValueError):
            self.handler_r.fileFormat = 123
        with self.assertRaises(ValueError):
            self.handler_r.fileFormat = None
    
    # def test_open(self):
    #     pass
    
    # def test_readFile(self):
    #     pass
    
    # def test_writeFile(self):
    #     pass

    
def run_tests():
    test_classes_to_run = [TestVPCData, TestFileHandler]
    
    loader = unittest.TestLoader()
    
    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)
    
    big_suite = unittest.TestSuite(suites_list)
    
    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)

if __name__ == "__main__":
    run_tests()