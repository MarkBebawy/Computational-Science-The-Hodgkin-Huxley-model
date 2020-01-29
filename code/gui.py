## This file implements the graphical user interface
## for the model. The code is inspired by the tutorial
## which can be found on: https://www.python-course.eu/tkinter_entries.php.

import tkinter as tk
import matplotlib.pyplot as plt
import experiments as expy
import validation as vali
import hh
import os

########### Entry validation functions to assert valid input values ################
class Validation:
    """This class implements validation methods for each entry widget."""
    def is_float(val):
        """This function returns true if val can be converted to a float."""
        try:
            float(val)
            return True
        except ValueError:
            return False

    def quick_val(value):
        """This function validates the input of the 'quick' entry."""
        return value.isdigit() and (int(value) == 0 or int(value) == 1)

    def num_method_steps_val(value):
        """This function validates the input of the size of time steps for numerical method entry."""
        return Validation.is_float(value) and 0 < float(value) and float(value) <= 10

    ## Option 1
    def inj_current_val(value):
        """This function validates the input of the injected current entry."""
        return Validation.is_float(value) and 0 <= float(value) and float(value) <= 150

    def inj_start_val(value):
        """This function validates the input of the start time current injection entry."""
        return value.isdigit() and 0 <= int(value)

    def inj_end_val(value):
        """This function validates the input of the end time for current injection entry."""
        return value.isdigit() and 0 <= int(value)

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
        return value.isdigit() and 0 < int(value) and int(value) <= 100

    def rest_pot_eps_val(value):
        """This function validates the input of the tolerance for resting potential entry."""
        return Validation.is_float(value) and 0 < float(value) and float(value) <= 15

    def run_time2_val(value):
        """This function validates the input of the run time (option 2) entry."""
        return value.isdigit() and 0 < int(value) and int(value) <= 50

    def inj_mean_val(value):
        """This function validates the input of the mean injection current strength."""
        return Validation.is_float(value) and 0 <= float(value) and float(value) <= 150

    def inj_var_val(value):
        """This function validates the input of the variance of injection current strength."""
        return Validation.is_float(value) and 0 <= float(value) and float(value) <= 50

    def dur_mean_val(value):
        """This function validates the input of the mean duration."""
        return Validation.is_float(value) and 0 <= float(value) and float(value) <= 100

    def dur_var_val(value):
        """This function validates the input of the variance of the duration."""
        return Validation.is_float(value) and 0 <= float(value) and float(value) <= 50

    def i_start_time_val(value):
        """This function validates the input of the injection start time."""
        return value.isdigit() and 0 <= int(value)

    def num_exps_val(value):
        """This function validates the input of the number of experiment iterations."""
        return value.isdigit() and 1 <= int(value) and int(value) <= 30

    def file_name_val(value):
        """All strings are valid file names."""
        return True
########### -------------------------- ################


def make_entries(screen, settings):
    """This function makes entries with keys, default values and labels from
    settings. It returns a dictionary with entry widgets as values."""
    entries = dict()

    # For each setting, create a text field and put it next to the
    # corresponding label.
    for i, (key, default, text) in enumerate(settings):
        row = tk.Frame(screen)
        label = tk.Label(row, width=50, text=text)
        entry = tk.Entry(row)
        entry.insert(0, default)

        row.pack(side=tk.TOP, fill=tk.X)
        label.pack(side=tk.LEFT)
        entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries[key] = entry

    return entries


def setup_start(screen):
    """This function makes a screen, adds all labels, entry
    widgets and returns the screen and the entry
    widgets."""
    # Strings, keys and default values for all fields.
    settings_general = [('quick', '1', 'Numerical method (RK4=0, Forw. Euler=1)'),
                        ('num_method_steps', '0.001', 'Size of time steps for\nnumerical method (in interval (0, 10])')]
    settings_op1 = [('inj_current', '20', 'Amount of injected current (range 0 - 150)'),
                    ('inj_start', '3', 'Start time for current injection'),
                    ('inj_end', '4', 'End time for current injection'),
                    ('temp', '6.3', 'Temperature (degrees celsius, interval [-60, 60])'),
                    ('run_time1', '20', 'Run time (miliseconds, interval (0, 100])')]
    settings_op2 = [('inj_mean', '20', 'Mean current strength, in interval [0, 150]'),
                    ('inj_var', '0', 'Variance of current strength, in interval [0, 50]'),
                    ('dur_mean', '1', 'Mean duration'),
                    ('dur_var', '0', 'Variance for duration, in interval [0, 50]'),
                    ('i_start_time', '0', 'Start time for current injection'),
                    ('min_temp', '6.3', 'Minimum temperature (celsius, interval [-60, 60])'),
                    ('max_temp', '46.3', 'Maximum temperature (celsius, interval [-60, 60])'),
                    ('temp_steps', '10', 'Amount of experiments points in\ntemperature range, integer between 1 and 100'),
                    ('rest_pot_eps', '10', 'Tolerance for resting potential, interval (0, 15]'),
                    ('num_exps', '3', 'Number of iterations per temperature, integer in [1, 30]'),
                    ('run_time2', '10', 'Run time per experiment (miliseconds, interval (0, 50])'),
                    ('file_name', '', ('File name to store/load results (empty: no results saved)\n'
                                       'Only enter names of files stored in \'stored_figs/\''))]
    welcome_str = ("Welcome to the Hodgkin-Huxley GUI.\n\nOption 1: One action potential "
        "can be simulated and plotted.\nOption 2: Temperature experiments "
        "can be run.\nModel verification shows model obeys all-or-nothing principle.\n\n"
        "When running either option, the variables of\nthe other option will be ignored.\n"
        "On wrong input, no simulation will run.\nSee terminal for how to fix this."
        "\n\n\nGeneral options")

    tk.Label(screen, text=welcome_str, font='bold').pack(side=tk.TOP)

    # Make widgets and text fields.
    ## General settings
    entries_general = make_entries(screen, settings_general)

    ## Options specific for one action potential simulation.
    tk.Label(screen, text="\nOption 1 variables", font='bold').pack(side=tk.TOP)
    entries_op1 = make_entries(screen, settings_op1)

    ## Options specific for temperature experiments.
    op2_title = ("\nOption 2 variables.\nInjected current is drawn from\n"
                 "a normal distribution for a normal distributed duration.\n"
                 "For determinism, use variance zero.")
    tk.Label(screen, text=op2_title, font='bold').pack(side=tk.TOP)
    entries_op2 = make_entries(screen, settings_op2)

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
        model.set_num_method(bool(int(entries_gen['quick'].get())), float(entries_gen['num_method_steps'].get()))
        model.set_injection_data(float(entries_op1['inj_current'].get()), int(entries_op1['inj_start'].get()),
                                int(entries_op1['inj_end'].get()))
        model.set_temperature(float(entries_op1['temp'].get()))
        model.set_run_time(int(entries_op1['run_time1'].get()))

        # Simulate model and show plot.
        model.solve_model()
        model.plot_results()
    print("------------------------------------------------------")


def sim_temp(entries_gen, entries_op2):
    """This function runs the temperature experiments and shows a plot,
    using the parameters enterded by the user."""
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

        model = hh.HodgkinHuxley()
        curr_params = expy.CurrentParameters()
        temp_exp = expy.TempExperiment()

        # Set parameters
        model.set_num_method(bool(int(entries_gen['quick'].get())), float(entries_gen['num_method_steps'].get()))
        temp_exp.set_temp_exp_data(float(entries_op2['min_temp'].get()), float(entries_op2['max_temp'].get()),
                                int(entries_op2['temp_steps'].get()), float(entries_op2['rest_pot_eps'].get()),
                                model, curr_params)
        curr_params.set_curr_data(float(entries_op2['inj_mean'].get()), float(entries_op2['inj_var'].get()),
                                float(entries_op2['dur_mean'].get()), float(entries_op2['dur_var'].get()),
                                int(entries_op2['i_start_time'].get()))
        model.set_run_time(int(entries_op2['run_time2'].get()))
        file_path = str(entries_op2['file_name'].get())

        # Simulate model and show plot.
        temp_exp.run(int(entries_op2['num_exps'].get()))

        # Store results in csv file, if file name specified.
        if file_path:
            temp_exp.store_csv("stored_figs/" + file_path)
        temp_exp.plot()
    print("------------------------------------------------------")


def model_verification():
    """This function runs the model verification and plots the result (all-or-nothing principle)."""
    print("Model verification: all-or-nothing principle. This could take some time...")
    ver_mod = vali.ValidationExperiment()
    ver_mod.run()
    ver_mod.plot()
    print("------------------------------------------------------")


def plot_temp(entries_gen, entries_op2):
    """This function plots the temperature experiments and shows a plot,
    using the parameters enterded by the user."""
    print("Plotting temperature experiments...")

    # Check if file path exists.
    file_path = 'stored_figs/' + str(entries_op2['file_name'].get())
    if not os.path.isfile(file_path):
        print(f"ERROR: File {file_path} does not exist!")
        return

    temp_exp = expy.TempExperiment()


    # Load results from csv file and plot figure.
    temp_exp.load_csv(file_path)
    temp_exp.plot()
    print("------------------------------------------------------")


def mainloop():
    """This function sets up a screen, handles all variables and
    calls the appropriate functions when buttons are pressed. It
    also creates these buttons."""
    screen = tk.Tk()
    entries_gen, entries_op1, entries_op2 = setup_start(screen)

    # Create buttons
    tk.Button(screen, text='Quit', command=quit).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(screen, text='Option 1\nSimulate action potential',
        command=(lambda e1=entries_gen, e2=entries_op1: sim_AP(e1, e2))).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(screen, text='Option 2\nRun and plot temperature experiments',
        command=(lambda e1=entries_gen, e2=entries_op2: sim_temp(e1, e2))).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(screen, text='Option 2\nPlot temperature experiments',
        command=(lambda e1=entries_gen, e2=entries_op2: plot_temp(e1, e2))).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(screen, text='Model verification', command=model_verification).pack(side=tk.LEFT, padx=5, pady=5)
    screen.mainloop()


if __name__ == "__main__":
    mainloop()
