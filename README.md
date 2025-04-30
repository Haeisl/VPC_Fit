Virtual Patient Cohorts
=======================
**A Python application for fitting mathematical models to medical data and generating virtual patient profiles**

---

## Overview
**Virtual Patient Cohorts** is a tool designed to simulate and analyze medical data through model fitting. Originally conceived to generate synthetic patient data, the project evolved into a robust fitting interface that allows medical researchers to:
- Import real-world datasets
- Define mathematical models (including ODEs)
- Fit those models to data using numerical methods
- Visualize and export results
This provides a flexible foundation for constructing virtual cohorts, particularly useful in domains where real patient data is limited or incomplete.

---

## Feature
- Model Fitting Support
  - Ordinary functions and first-order differential equations
  - Custom model equations via symbolic input
  - Fit using least-squares and BFGS optimization
- Intuitive GUI (built with ``customtkinter``)
  - Easy data input (.csv, .xlsx)
  - Real-time feedback and error handling
  - Plotting of model vs. data
- Usability-Focused Design
  - Clear validation messages
  - Modular code structure (MVC pattern)
  - Comprehensive logging for debugging
- Extensibility
  - Add custom fitting algorithms or visualization modules
  - Object-oriented structure for maintainability
 
---

## Installation
```cmd
  git clone https://github.com/Haeisl/VPC_Fit.git
  cd VPC_Fit
  pip install -r requirements.txt
  python main.py
```

---

## Usage
1. Upload your dataset
2. Enter your model as a function or differential equation
3. Select variables and configure fitting parameters
4. Run fitting process
5. Save output for documentation or downstream analysis

Supported fitting types:
- Function fitting: ``f(x, p1, p2, ...)``
- First-order ODE fitting: ``dy/dx = f(x, y, p1, ...)``

---

## Example Use Case
> A medical researcher wants to test a pharmacokinetic model against clinical data with limited samples. By importing the dataset and entering the ODE model, they can fit the parameters, visualize prediction error, and simulate similar virtual patients.

---

## Documentation
Full documentation available at:
https://vpc-fit.readthedocs.io/en/latest/

---

## Credits
Developed by **Alisa Ebert** and **David Hasse** as part of a software practical at Heidelberg University.
