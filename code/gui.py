# This file implements the graphical user interface
# for the model. The code is inspired by the tutorial
# which can be found on:
# https://www.python-course.eu/tkinter_entries.php.
#
# TODO: Ideas:
#           - Default values in entry widgets
#           - Reset button to use default values
#           - Opmaak
#           - Restrict values & types in entry widgets
#           - Pijltjes in text widget for increase/decrease
#           - Only allow certain types in widgets (+setter for range).

import tkinter as tk
import matplotlib.pyplot as plt
import expy
import hh

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
    settings_general = ["Amount of injected current", "Start time for current injection",
        "End time for current injection", "Numerical method (RK4=0, Forw. Euler=1)",
        "Size of time steps for numerical method"]
    settings_op1 = ["Temperature (degrees celsius)", "Run time (miliseconds)"]
    settings_op2 = ["Minimum temperature (degrees celsius)", "Maximum temperature (degrees celsius)",
        "Amount of experiments points in temperature range", "Tolerance for resting potential",
        "Run time per experiment (miliseconds)"]

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
        "can be run.\n\nWhen running either option, the variables of\nthe other option will be ignored."
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
    print("Simulating one action potential. This could take some time...")
    model = hh.HodgkinHuxley()

    # Set general parameters
    # TODO: controleer input, bool(1) = True, bool(0) = False.
    model.set_injection_data(float(entries_gen['inj_current'].get()), int(entries_gen['inj_start'].get()),
                             int(entries_gen['inj_end'].get()))
    model.set_num_method(bool(entries_gen['quick'].get()), float(entries_gen['num_method_steps'].get()))
    model.set_temperature(float(entries_op1['temp'].get()))
    model.set_run_time(int(entries_op1['run_time1'].get()))

    t, y = model.solve_model()
    plt.plot(t, y[:,0])
    plt.show()


def mainloop():
    """This function sets up a screen, handles all variables and
    calls the appropriate functions when buttons are pressed. It
    also creates these buttons."""
    screen = tk.Tk()
    entries_gen, entries_op1, entries_op2 = setup_start(screen)

    # Create buttons
    # TODO: controleer waarden.
    tk.Button(screen, text='Quit', command=screen.quit).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(screen, text='Simulate action potential',
        command=(lambda e1=entries_gen, e2=entries_op1: sim_AP(e1, e2))).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(screen, text='Run temperature experiments', command="").pack(side=tk.LEFT, padx=5, pady=5)

    screen.mainloop()


if __name__ == "__main__":
    mainloop()
