import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from random import uniform
from pathlib import Path
from datetime import datetime

noise = uniform(0,4)

def function_no_noise(t):
    return 2*t**3 + 3.25*t**2 + 5*t + 1.7

def function_end_noise(t):
    return 2*t**3 + 3.25*t**2 + 5*t + 1.7+noise

def function_all_noise(t):
    return (2+noise)*t**3 + (3.25+noise)*t**2 + (5+noise)*t + (1.7+noise)

def test_func(t):
    return 1.19*t**3 + 15.97*t**2 - 51.72*t + 75.09


def valid_name() -> str:
    now = datetime.now()
    return now.strftime("%Y-%m-%d-sample-data-from-%Hh%Mm")


def create_excel() -> None:
    dir_path = Path("./misc/")
    name = valid_name() + ".xlsx"
    file_path = dir_path / name

    x = np.linspace(0,10,100)
    y = function_no_noise(x)
    noise = np.random.normal(0, 100, len(y))
    y_noise = y + noise

    data = {
        "Lauf": x,
        "Egal": y_noise
    }

    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False, header=False)


def plot() -> None:
    x = np.linspace(0,10,100)
    y1 = function_no_noise(x)
    y2 = function_end_noise(x)
    y3 = function_all_noise(x)

    noise = np.random.normal(0, 100, len(y1))
    y4 = y1 + noise

    y5 = test_func(x)
    # plt.plot(x, y1, label="no noise")
    # plt.plot(x, y2, label="end noise")
    # plt.plot(x, y3, label="all noise")
    plt.plot(x, y5, label="woah")
    plt.xlabel('x-axis')
    plt.ylabel('y-axis')
    plt.legend()
    plt.grid(True)
    plt.show()


def main() -> None:
    # create_excel()
    plot()


if __name__ == '__main__':
    main()