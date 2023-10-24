import tkinter as tk
from tkinter import filedialog
from FileHandler import FileHandler
from VPCData import VPCData
from ModelFitter import ModelFitter


class ModelEquationWindow(tk.Toplevel):
    def __init__(self, mainWindow, modelEquationTextVar):
        super().__init__(mainWindow)
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        windowWidth = 400
        windowHeight = 160
        centerX = int(screenWidth/2 + 460/2 + 1)
        centerY = int(screenHeight/2 - 260/4)
        self.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')
        
        self.modelEqTextVar = modelEquationTextVar
        
        # text
        text = "You can modify the model equation below.\nPlease only use standard pythonic notation for the equation.\nThe independent variable should be called 't'"
        self.explanatoryText = tk.Message(self, text=text, width=windowWidth)
        
        # labels
        self.modelLabel = tk.Label(self, text='Enter new model equation:')
        
        # entries
        self.modelEntry = tk.Entry(self)
        
        # button
        self.updateButton = tk.Button(self, text='Update', command=self.updateEquationText)
        
        # grid
        self.explanatoryText.grid(column=0, row=0, columnspan=3, sticky=tk.NSEW, padx=10, pady=10)
        self.modelLabel.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=(10,5))
        self.modelEntry.grid(column=1, row=1, sticky=tk.NSEW, padx=10, pady=(10,5))
        self.updateButton.grid(column=2, row=2, sticky=tk.NSEW, ipadx=10, ipady=5, padx=10, pady=0)
    
    def updateEquationText(self):
        newEquationText = self.modelEntry.get()
        self.modelEqTextVar.set(newEquationText)
        self.destroy()

class ResultsWindow(tk.Toplevel):
    def __init__(self, mainWindow, message):
        tk.Toplevel.__init__(mainWindow)
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        windowWidth = 320
        windowHeight = 120
        centerX = int(screenWidth/2 - windowWidth/2 + 425/2)
        centerY = int(screenHeight/2 - 240/4)
        self.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')
        
        # labels
        self.modelParameters = tk.StringVar(self)
        self.modelParameters.set(f"f(t) = {message[0]}*t + {message[1]}")
        self.modelParametersLabel = tk.Label(self, textvariable=self.modelParameters)
        
        # grid
        self.modelParametersLabel.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

class MainApplication(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('Virtual Patient Cohort Generator')
        
        # member variables
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
        self.funcParamsLabel = tk.Label(text='#Function Parameters:')
        self.resComponentsLabel = tk.Label(text='#Result Components:')
        self.modelTypeLabel = tk.Label(text='Model Type:')
        self.dataInputLabel = tk.Label(text='Datapoints:')
        self.indexTimeLabel = tk.Label(text='Use Indexing for time:')
        self.useFirstRowLabel = tk.Label(text='Include First Row:')
        # self.amountToGenerateLabel = tk.Label(text='Amount To Generate:')

        # entries
        vcmd = (self.register(self.validateEntry))
        # self.funcParams = tk.StringVar()
        # self.funcParamsEntry = tk.Entry(textvariable=self.funcParams, validate='all', validatecommand=(vcmd, '%P'), width=5)
        self.funcParams = tk.IntVar(value=1)
        self.funcParamsEntry = tk.Entry(textvariable=self.funcParams, validate='all', validatecommand= (vcmd, '%P'), width=5)
        # self.resComponents = tk.StringVar()
        # self.resComponentsEntry = tk.Entry(textvariable=self.resComponents, validate='all', validatecommand=(vcmd, '%P'), width=5)
        self.resComponents = tk.IntVar(value=1)
        self.resComponentsEntry = tk.Entry(textvariable=self.resComponents, validate='all', validatecommand= (vcmd, '%P'), width=5)
        
        # checkboxes
        self.useIndexingTime = tk.BooleanVar()
        self.indexTimeCheck = tk.Checkbutton(variable=self.useIndexingTime)
        self.useFirstRow = tk.BooleanVar()
        self.useFirstRowCheck = tk.Checkbutton(variable=self.useFirstRow)
        
        # constants / strings
        OPTIONS = [
            'Linear',
            'Polynomial',
            'Exponential',
            'Trigonometric',
            'Differential'
        ]
        EQUATIONS = [
            'A*t + B',              # linear
            'A*t^2 + B*t + C',      # polynomial
            'A*e^(B*t) + C',        # exponential
            'A*sin(B*t + C) + D',   # trigonometric
            'dy/dx = f(x, y)'       # differential
        ]

        # drop down menu
        self.modelTypeChoice = tk.StringVar()
        self.modelTypeChoice.set(OPTIONS[0])
        self.dataTypeMenu = tk.OptionMenu(self, self.modelTypeChoice, *OPTIONS)

        # buttons
        self.fileName = tk.StringVar(self, 'Browse...')
        self.dataInputButton = tk.Button(textvariable=self.fileName, command=self.browseFiles)
        self.generateDataButton = tk.Button(text='Compute Parameters', command=self.computeParameters)
        self.modelEquation = tk.StringVar()
        self.modelEquation.set(EQUATIONS[0])
        self.modelEditButton = tk.Button(textvariable=self.modelEquation, command=self.openModelEquationChangeWindow)
        
        def updateButton(*args):
            selectedIdx = OPTIONS.index(self.modelTypeChoice.get())
            self.modelEquation.set(EQUATIONS[selectedIdx])
        
        self.modelTypeChoice.trace('w', updateButton)

        # placement in window
        labelPaddingX = (20,5)
        
        # 1st row
        self.funcParamsLabel.grid(column=0, row=0, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=(20,5))
        self.funcParamsEntry.grid(column=2, row=0, sticky=tk.W, padx=0, pady=(20,5))
        self.resComponentsLabel.grid(column=3, row=0, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=(20,5))
        self.resComponentsEntry.grid(column=5, row=0, sticky=tk.W, padx=(0,20), pady=(20,5))
        
        # 2nd row
        self.modelTypeLabel.grid(column=0, row=1, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=5)
        self.dataTypeMenu.grid(column=2, row=1, columnspan=4, sticky=tk.W, ipadx=20, padx=(0,20), pady=(5,0))

        # 3rd row
        self.modelEditButton.grid(column=2, row=2, columnspan=4, sticky=tk.W, ipadx=20, padx=(2,0), pady=(0,5))
        
        # 4th row
        self.dataInputLabel.grid(column=0, row=3, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=5)
        self.dataInputButton.grid(column=2, row=3, columnspan=4, sticky=tk.W, ipadx=20, padx=(2,20), pady=5)
        
        # 5th row
        self.indexTimeLabel.grid(column=0, row=4, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=5)
        self.indexTimeCheck.grid(column=2, row=4, sticky=tk.W, padx=(0,20), pady=5)
        
        # 6th row
        self.useFirstRowLabel.grid(column=0, row=5, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=0)
        self.useFirstRowCheck.grid(column=2, row=5, sticky=tk.W, padx=(0,20), pady=0)
        
        # 7th row
        self.generateDataButton.grid(column=4, row=6, columnspan=2, sticky=tk.W, ipadx=20, padx=(5,20), pady=(10,5))
        
    def openModelEquationChangeWindow(self):
        """
        Opens a new window for the user to change the default model equation to a custom one
        """
        modelEquationWindow = ModelEquationWindow(self, self.modelEquation)
    
    def openResultsWindow(self, parameters):
        resultsWindow = ResultsWindow(self, parameters)
        
    def validateEntry(self, P: str):
        """
        Validation method to ensure only digits are entered for #Function Parameters and #Result Components

        Args:
            P (str): character that user tries to enter
        Returns:
            True: if entered character is a digit or empty (e.g. backspace)
            False: otherwise
        """
        return P.isdigit() or P == ''
    
    def browseFiles(self):
        """
        Opens filedialog for user to specify the location of the file.
        Sets fileName and filePath if user did not cancel the dialog.
        """
        fp = filedialog.askopenfile()
        if fp is not None:
            fn = fp.name.split('/')[-1]
            self.fileName.set(fn)
            self.filePath = fp.name

    def computeParameters(self):
        """
        Main functionality of the app. Computes Parameters of the model given the type of model to fit and a dataset.

        Raises:
            ValueError: can't fit a model if there is no filepath specified and thus no data to be fitted into a model.
        """
        if self.filePath is None:
            raise ValueError("Did not specify a filepath")
        fh = FileHandler.ReadMode(self.filePath)
        fh.readFile()
        vpcdList = fh.formatData(self.useFirstRow.get())
        
        modelFitter = ModelFitter()
        
        modelEquation = self.modelEquation.get()
        funcParams = self.funcParams.get()
        resComps = self.resComponents.get()
        
        # , numFunctionParameters=funcParams, numResultComponents=resComps
        modelFitter.fit(data=vpcdList, equation=modelEquation)
        
        #print(f"f(t) = {modelFitter.coefficients[0]}*t + {modelFitter.intercept}")
        
        #self.openResultsWindow([str(modelFitter.coefficients[0]), str(modelFitter.intercept)])
        # vpcdList:
        # 0: empty file
        # 1: assumption: not timeVec, only measurementVec
        # 2: assumption: timeVec and measurementVec
        # >2: unclear; assumption: timeVec, measurementVec, and more?
        
        
if __name__ == '__main__':
    main = MainApplication()
    main.mainloop()