# This file implements the graphical user interface
# for the model. The code is inspired by the tutorial
# which can be found on:
# https://www.python-course.eu/tkinter_entries.php.

import tkinter as tk
import matplotlib.pyplot as plt
import expy
import hh

########### Entry validation functions ################
class Validation:
    """This class implements validation methods for each entry widget."""
    def is_float(val):
        """This function returns true if val can be converted to a float."""
        try:
            float(val)
            return True
        except ValueError:
            return False

    def inj_current_val(value):
        """This function validates the input of the injected current entry."""
        return Validation.is_float(value) and 0 <= float(value) and float(value) <= 150

    def inj_start_val(value):
        """This function validates the input of the start time current injection entry."""
        return value.isdigit() and 0 <= int(value)

    def inj_end_val(value):
        """This function validates the input of the end time for current injection entry."""
        return value.isdigit() and 0 <= int(value)

    def quick_val(value):
        """This function validates the input of the 'quick' entry."""
        return value.isdigit() and (int(value) == 0 or int(value) == 1)

    def num_method_steps_val(value):
        """This function validates the input of the size of time steps for numerical method entry."""
        return Validation.is_float(value) and 0 < float(value) and float(value) <= 10

    ## Option 1
    def temp_val(value):
        """This function validates the temperature entry."""
        return Validation.is_float(value) and -60 <= float(value) and float(value) <= 60

    def run_time1_val(value):
        """This function validates the run time entry."""
        return value.isdigit() and 0 < int(value) and int(value) <= 100

    ## Option 2
    def min_temp_val(value):
        """This function validates the minimum temperature entry."""
        return Validation.temp_val(value)

    def max_temp_val(value):
        """This function validates the maximum temperature entry."""
        return Validation.temp_val(value)

    def temp_steps_val(value):
        """This function validates the input of the amount of experiments points entry."""
        return value.isdigit() and 0 < int(value) and int(value) <= 20

    def rest_pot_eps_val(value):
        """This function validates the input of the tolerance for resting potential entry."""
        return Validation.is_float(value) and 0 < float(value) and float(value) <= 15

    def run_time2_val(value):
        """This function validates the input of the run time (option 2) entry."""
        return value.isdigit() and 0 < int(value) and int(value) <= 10
########### -------------------------- ################


def make_entries(screen, keys, settings, defaults):
    """This function makes entries with labels from settings and default
    values from defaults. It returns dictionaries with keys from 'keys'
    and the entry widgets as values."""
    entries = dict()

    # For each setting, create a text field and put it next to the
    # corresponding label.
    for i, setting in enumerate(settings):
        row = tk.Frame(screen)
        label = tk.Label(row, width=50, text=setting)
        entry = tk.Entry(row)
        entry.insert(0, defaults[i])

        row.pack(side=tk.TOP, fill=tk.X)
        label.pack(side=tk.LEFT)
        entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries[keys[i]] = entry

    return entries


def setup_start(screen):
    """This function makes a screen, adds all labels, entry
    widgets and returns the screen and the entry
    widgets."""
    # Strings for all fields.
    settings_general = ["Amount of injected current (range 0 - 150)", "Start time for current injection",
        "End time for current injection", "Numerical method (RK4=0, Forw. Euler=1)",
        "Size of time steps for\nnumerical method (in interval (0, 10])"]
    settings_op1 = ["Temperature (degrees celsius, interval [-60, 60])", "Run time (miliseconds, interval (0, 100])"]
    settings_op2 = ["Minimum temperature (celsius, interval [-60, 60])",
        "Maximum temperature (celsius, interval [-60, 60])",
        "Amount of experiments points in\ntemperature range, integer between 1 and 20",
        "Tolerance for resting potential, interval (0, 15]",
        "Run time per experiment (miliseconds, interval (0, 10])"]

    # Keys for all fields.
    keys_general = ["inj_current", "inj_start", "inj_end", "quick", "num_method_steps"]
    keys_op1 = ["temp", "run_time1"]
    keys_op2 = ["min_temp", "max_temp", "temp_steps", "rest_pot_eps", "run_time2"]

    # Default values.
    defaults_general = ['20', '3', '4', '0', '0.0001']
    defaults_op1 = ['6.3', '10']
    defaults_op2 = ['6.3', '46.3', '10', '10', '10']

    welcome_str = ("Welcome to the Hodgkin-Huxley GUI.\n\nOption 1: One action potential "
        "can be simulated and plotted.\nOption 2: Temperature experiments "
        "can be run.\n\nWhen running either option, the variables of\nthe other option will be ignored.\n"
        "On wrong input, no simulation will run.\nSee terminal for how to fix this."
        "\n\n\nGeneral options")

    tk.Label(screen, text=welcome_str, font='bold').pack(side=tk.TOP)

    # Make widgets and text fields.
    ## General settings
    entries_general = make_entries(screen, keys_general, settings_general, defaults_general)

    ## Options specific for one action potential simulation.
    tk.Label(screen, text="\nOption 1 variables", font='bold').pack(side=tk.TOP)
    entries_op1 = make_entries(screen, keys_op1, settings_op1, defaults_op1)

    ## Options specific for temperature experiments.
    tk.Label(screen, text="\nOption 2 variables", font='bold').pack(side=tk.TOP)
    entries_op2 = make_entries(screen, keys_op2, settings_op2, defaults_op2)

    return entries_general, entries_op1, entries_op2


def sim_AP(entries_gen, entries_op1):
    """This function simulates an action potential and shows a plot, using
    the parameters entered by the user."""
    model = hh.HodgkinHuxley()
    valid = True

    # For every general entry, get value and validate.
    for entry in entries_gen:
        validate_func = entry + "_val"

        # If invalid input print error and set valid False, such that the simulation
        # won't be run.
        if not getattr(Validation, validate_func)(entries_gen[entry].get()):
            print(f"ERROR: Entry {entry} contains invalid input.\nWon't run simulation.")
            valid = False

    # For every option specific entry, get value and validate.
    for entry in entries_op1:
        validate_func = entry + "_val"

        # If invalid input print error and set valid False, such that the simulation
        # won't be run.
        if not getattr(Validation, validate_func)(entries_op1[entry].get()):
            print(f"ERROR: Entry {entry} contains invalid input.\nWon't run simulation.")
            valid = False

    if valid:
        print("Simulating one action potential. This could take some time...")

        # Set parameters
        model.set_injection_data(float(entries_gen['inj_current'].get()), int(entries_gen['inj_start'].get()),
                                int(entries_gen['inj_end'].get()))
        model.set_num_method(bool(entries_gen['quick'].get()), float(entries_gen['num_method_steps'].get()))
        model.set_temperature(float(entries_op1['temp'].get()))
        model.set_run_time(int(entries_op1['run_time1'].get()))

        # Simulate model and show plot.
        t, y = model.solve_model()
        plt.plot(t, y[:,0])
        plt.show()
    print("------------------------------------------------------")


def sim_temp(entries_gen, entries_op2):
    """This function runs the temperature experiments and shows a plot,
    using the parameters enterded by the user."""
    model = hh.HodgkinHuxley()
    valid = True

    # For every general entry, get value and validate.
    for entry in entries_gen:
        validate_func = entry + "_val"

        # If invalid input print error and set valid False, such that the simulation
        # won't be run.
        if not getattr(Validation, validate_func)(entries_gen[entry].get()):
            print(f"ERROR: Entry {entry} contains invalid input.\nWon't run simulation.")
            valid = False

    # For every option specific entry, get value and validate.
    for entry in entries_op2:
        validate_func = entry + "_val"

        # If invalid input print error and set valid False, such that the simulation
        # won't be run.
        if not getattr(Validation, validate_func)(entries_op2[entry].get()):
            print(f"ERROR: Entry {entry} contains invalid input.\nWon't run simulation.")
            valid = False

    if valid:
        print("Running temperature experiments. This could take some time...")

        # Set parameters
        model.set_injection_data(float(entries_gen['inj_current'].get()), int(entries_gen['inj_start'].get()),
                                int(entries_gen['inj_end'].get()))
        model.set_num_method(bool(entries_gen['quick'].get()), float(entries_gen['num_method_steps'].get()))
        model.set_temp_exp_data(float(entries_op2['min_temp'].get()), float(entries_op2['max_temp'].get()),
                                int(entries_op2['temp_steps'].get()), float(entries_op2['rest_pot_eps'].get()))
        model.set_run_time(int(entries_op2['run_time2'].get()))

        # Simulate model and show plot.
        temps, ap_times = expy.speedTemperature(model)
        expy.plot(temps, ap_times)
    print("------------------------------------------------------")


def mainloop():
    """This function sets up a screen, handles all variables and
    calls the appropriate functions when buttons are pressed. It
    also creates these buttons."""
    screen = tk.Tk()
    entries_gen, entries_op1, entries_op2 = setup_start(screen)

    # Create buttons
    tk.Button(screen, text='Quit', command=screen.quit).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(screen, text='Option 1\nSimulate action potential',
        command=(lambda e1=entries_gen, e2=entries_op1: sim_AP(e1, e2))).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(screen, text='Option 2\nRun temperature experiments',
        command=(lambda e1=entries_gen, e2=entries_op2: sim_temp(e1, e2))).pack(side=tk.LEFT, padx=5, pady=5)

    screen.mainloop()


if __name__ == "__main__":
    mainloop()
