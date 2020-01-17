# This file implements the graphical user interface
# for the model. The code is inspired by the tutorial
# which can be found on:
# https://www.python-course.eu/tkinter_entry_widgets.php.
#
# TODO: Ideas:
#           - Default values in entry widgets
#           - Reset button to use default values
#           - Opmaak
#           - Restrict values in entry widgets
#           - Pijltjes in text widget for increase/decrease
#           - Only allow certain types in widgets (+setter for range).

import tkinter as tk
import expy
import hh

def setup_start():
    """This function makes a screen, adds all labels, entry
    widgets and returns the screen and the entry
    widgets."""
    screen = tk.Tk()
    welcome_str = ("Welcome to the Hodgkin-Huxley GUI.\nOption 1: One action potential "
        "can be simulated and plotted.\nOption 2: Temperature experiments "
        "can be run.\n\nGeneral options")
    tk.Label(screen, text=welcome_str).grid(row=0)

    ## Options for current injection.
    tk.Label(screen, text="Amount of injected current").grid(row=1)
    tk.Label(screen, text="Start time for current injection").grid(row=2)
    tk.Label(screen, text="End time for current injection").grid(row=3)

    ## Options for numerical method.
    tk.Label(screen, text="Numerical method (RK4=0, Forw. Euler=1)").grid(row=4)
    tk.Label(screen, text="Size of time steps for numerical method").grid(row=5)

    ## Options specific for one action potential simulation.
    tk.Label(screen, text="\nOption 1 variables (option 2 will be ignored)").grid(row=6)
    tk.Label(screen, text="Temperature (degrees celsius)").grid(row=7)
    tk.Label(screen, text="Run time (miliseconds)").grid(row=8)

    ## Options specific for temperature experiments.
    tk.Label(screen, text="\nOption 2 variables (option 1 will be ignored)").grid(row=9)
    tk.Label(screen, text="Minimum temperature (degrees celsius)").grid(row=10)
    tk.Label(screen, text="Maximum temperature (degrees celsius)").grid(row=11)
    tk.Label(screen, text="Amount of experiments points in temperature range").grid(row=12)
    tk.Label(screen, text="Tolerance for resting potential").grid(row=13)
    tk.Label(screen, text="Run time per experiment (miliseconds)").grid(row=14)

    # XXX: Change this if variables are changed.
    num_rows = 15
    title_rows = [0, 6, 9]
    variable_rows = [i for i in range(num_rows) if i not in title_rows]

    # Make a list of entry widgets.
    # XXX: default values.
    entry_widgets = list()
    default_values = ['20', '3', '4', '0', '0.0001', '6.3', '10', '6.3', '46.3', '10', '10', '10']

    for indx, row in enumerate(variable_rows):
        entry_widgets.append(tk.Entry(screen))
        entry_widgets[indx].grid(row=row, column=1)
        entry_widgets[indx].insert("end", default_values[indx])

    return screen, entry_widgets, num_rows


def mainloop():
    """This function sets up a screen, handles all variables and
    calls the appropriate functions when buttons are pressed. It
    also creates these buttons."""
    screen, entry_widgets, num_rows = setup_start()

    # Create buttons
    tk.Button(screen, text='Quit', command=screen.quit).grid(row=num_rows, column=0)
    tk.Button(screen, text='Simulate action potential', command="").grid(row=num_rows, column=1)
    tk.Button(screen, text='Run temperature experiments', command="").grid(row=num_rows, column=2)

    screen.mainloop()

if __name__ == "__main__":
    mainloop()
