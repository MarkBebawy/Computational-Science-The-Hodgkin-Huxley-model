# This file implements the graphical user interface
# for the model. The code is inspired by the tutorial
# which can be found on:
# https://www.python-course.eu/tkinter_entry_widgets.php.

import tkinter as tk

def setup_start():
    """This function makes a screen, adds all labels, entry
    widgets and text buttons and shows the window to the user."""
    screen = tk.Tk(screenName="Hodgkin-Huxley model implementation")
    welcome_str = ("Welcome to the Hodgkin-Huxley GUI.\nOption 1: One action potential"
        "can be simulated and plotted.\nOption 2: Temperature experiments"
        "can be run.")
    tk.Label(screen, text=welcome_str).grid(row=0)

    # Options for current injection.
    tk.Label(screen, text="Amount of injected current").grid(row=1)
    tk.Label(screen, text="Start time for current injection").grid(row=2)
    tk.Label(screen, text="End time for current injection").grid(row=3)

    # Options for numerical method.
    tk.Label(screen, text="Numerical method (RK4=0, Forw. Euler=1)").grid(row=4)
    tk.Label(screen, text="Size of time steps for numerical method").grid(row=5)

    # Options specific for one action potential simulation.
    tk.Label(screen, text="Option 1 variables (option 2 will be ignored)").grid(row=6)
    tk.Label(screen, text="Temperature (degrees celsius)").grid(row=7)
    tk.Label(screen, text="Run time (miliseconds)").grid(row=8)

    # Options specific for temperature experiments.
    tk.Label(screen, text="Option 2 variables (option 1 will be ignored)").grid(row=9)
    tk.Label(screen, text="Minimum temperature (degrees celsius)").grid(row=10)
    tk.Label(screen, text="Maximum temperature (degrees celsius)").grid(row=11)
    tk.Label(screen, text="Amount of experiments points in temperature range").grid(row=12)
    tk.Label(screen, text="Tolerance for resting potential").grid(row=13)

    # Make entry widget for every variable.
    num_vars = 12
    entry_widgets = list()

    for i in range(num_vars):
        pass
