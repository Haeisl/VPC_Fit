import tkinter as tk
from tkinter import filedialog
from .FileHandler import FileHandler
from .VPCData import VPCData
from .ModelFitter import ModelFitter


class ResultsWindow(tk.Toplevel):
    """This is a class to handle the functionality of the interface in connection with the presentation of the results 
    """
    def __init__(self, mainWindow, message):
        """Constructor method

        :param mainWindow: the underlying main interface window
        :type mainWindow: MainApplication class object
        :param message: final equation with the calculated fitted parameters
        :type message: list
        """
        super().__init__(mainWindow)
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        windowWidth = 320
        windowHeight = 120
        centerX = int(screenWidth/2 - windowWidth/2 + 425/2)
        centerY = int(screenHeight/2 - 240/4)
        self.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')

        # labels
        self.finalEquation = tk.StringVar(self)
        self.finalEquation.set(f"f(t) = {message[0]}*t + {message[1]}")
        self.finalEquationLabel = tk.Label(self, textvariable=self.finalEquation)

        # grid
        self.finalEquationLabel.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
    
    def download():
        """opens filedialog for user to specify the location for the file with the results to be written if the user did not cancel the dialog
        
        This function combines the functionality to write the results into a file and save it on the computer
        """
        pass

    def restart():
        """sets the program to it's default state
        """
        pass


class MainApplication(tk.Tk):
    """This is a class to handle the functionality of the interface
    """

    def __init__(self):
        """Constructor method

        :param filePath: path to the file to be read or written
        :type filePath: str
        :param funcParams: parameters of the function to be fitted
        :type funcParams: tk.StringVar()
        :param numResComps: number of components of the result
        :type numResComp: tk.StringVar()
        :param fileName: name of the file to be read or written
        :type fileName: tk.StringVar()
        :param modelEquation: equation of the function to be fitted
        :type modelEquation: tk.StringVar()
        """
        tk.Tk.__init__(self)
        self.title('Virtual Patient Cohort Generator')
        self.filePath = None

        # setting window geometry relative to screen geometry
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        windowWidth = 460
        windowHeight = 260
        centerX = int(screenWidth/2 - windowWidth/2)
        centerY = int(screenHeight/2 - windowHeight/2)
        self.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        # labels
        self.equationLabel = tk.Label(text="Equation:")
        self.parameterLabel = tk.Label(text="What Parameter:")
        self.resComponentsLabel = tk.Label(text="# Result Components:")
        self.dataInputLabel = tk.Label(text="Data:")

        # entries
        self.equationEntry = tk.Entry()
        self.parameterEntry = tk.Entry()

        vcmd = (self.register(self.validateEntry))
        self.resComponents = tk.IntVar(value=1)
        self.resComponentsEntry = tk.Entry(textvariable=self.resComponents, validate='all', validatecommand= (vcmd, '%P'), width=5)

        # buttons
        self.fileName = tk.StringVar(self, 'Browse...')
        self.dataInputButton = tk.Button(textvariable=self.fileName, command=self.browseFiles)
        self.generateDataButton = tk.Button(text='Compute Parameters', command=self.computeParameters)

        # placement in window
        labelPaddingX = (20,5)

        # 1st row
        self.equationLabel.grid(column=0, row=0, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=5)
        self.equationEntry.grid(column=2, row=0, sticky=tk.W, padx=0, pady=5)

        # 2nd row
        self.parameterLabel.grid(column=0, row=1, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=5)
        self.parameterEntry.grid(column=2, row=1, sticky=tk.W, padx=0, pady=5)

        # 3rd row
        self.resComponentsLabel.grid(column=0, row=2, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=5)
        self.resComponentsEntry.grid(column=2, row=2, sticky=tk.W, padx=(0,20), pady=5)

        # 4th row
        self.dataInputLabel.grid(column=0, row=3, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=5)
        self.dataInputButton.grid(column=2, row=3, columnspan=4, sticky=tk.W, ipadx=20, padx=(2,20), pady=5)

        # 5th row
        self.generateDataButton.grid(column=2, row=4, columnspan=2, sticky=tk.E, ipadx=20, padx=(5,20), pady=(10,5))

    def openResultsWindow(self, parameters):
        """returns a ResultWindow object to present the resulting fitted parameters

        :param parameters: the calculated parameters
        :type parameters: list[float]
        """
        resultsWindow = ResultsWindow(self, parameters)

    def validateEntry(self, P: str):
        """validation method to ensure only digits are entered for #FunctionParameters and #ResultComponents

        :param P: character that user tries to enter
        :type P: str
        :return: true, if entered character is a digit or empty (e.g. backspace), false otherwise
        :rtype: bool
        """
        return P.isdigit() or P == ''
    
    def browseFiles(self):
        """opens filedialog for user to specify the location of the file and sets file name and file path if the user did not cancel the dialog
        """
        fp = filedialog.askopenfile()
        if fp is not None:
            fn = fp.name.split('/')[-1]
            self.fileName.set(fn)
            self.filePath = fp.name
    
    def computeParameters(self):
        """calculates the desired parameters based on the requirements provided by the user
        """
        self.openResultsWindow([2, 3])
