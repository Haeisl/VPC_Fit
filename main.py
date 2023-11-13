from src.app import MainApplication
from src.ModelFitter import ModelFitter
from sympy import symbols
def main():
    app = MainApplication()
    app.mainloop()

if __name__ == '__main__':
    mf = ModelFitter()
    func = mf.stringToFunction('a**t + b')
    a = 2
    b = 3
    t = 4
    res = func(symbols('t'))
    print(res)
    #main() 
    