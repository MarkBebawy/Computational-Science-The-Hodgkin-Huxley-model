## Functions to generate figures used in report.

import hh
import experiments as expy
import validation as vali
import tools
import os
import csv
import matplotlib.pyplot as plt
import numpy as np

def multiple_ap_plot():
    """Plots 5 action potentials using our standard parameters at temperatures
    from 15 to 45 degrees Celcius."""
    x = hh.HodgkinHuxley()
    x.set_run_time(2.5)
    x.plot_multiple_ap(15, 45, 5)

def large_temp_exp():
    """Runs large temperature with 100 tests and stores result (this can also be done with the GUI but
    this does not store results)"""
    model = hh.HodgkinHuxley()
    curr_params = expy.CurrentParameters()
    temp_exp = expy.TempExperiment()

    # Test temperatures between 5 and 45 degrees. Test 100 temperatures,
    # with 1 test per temperature (since experiment is deterministic)
    temp_exp.set_temp_exp_data(5, 45, 100, 1, model, curr_params)

    # Inject 50 nA/cm^2, starting at t=0, for 1ms, with no variance.
    curr_params.set_curr_data(50, 0, 1, 0, 0)
    model.set_run_time(20)

    # Simulate model and show plot.
    temp_exp.run(1)
    temp_exp.store_csv("results_100_deter_1.csv")
    plot_temp_exp_polyfit()


def plot_temp_exp_polyfit():
    """Load results from large temperature experiment and show."""
    # Read out file
    file_name = "results_100_deter_1.csv"
    assert os.path.isfile(file_name)
    ts = []
    ys = []
    with open(file_name, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            ts.append(float(row[0]))
            ys.append(float(row[1]))

    # Find first index where graph stops decreasing
    ind_fit = 0
    y_prev = 1000
    for i, y in enumerate(ys):
        if y > y_prev:
            ind_fit = i
            break
        y_prev = y
    assert ind_fit > 0

    # Fit degree 2 and 3 polynomial through the points where the graph
    # is decreasing
    ts_interp = ts[:ind_fit]
    ys_interp = ys[:ind_fit]
    print(ys_interp)
    print(ys[ind_fit])
    z2 = np.polyfit(ts_interp, ys_interp, 2)
    z3 = np.polyfit(ts_interp, ys_interp, 3)
    p2 = np.poly1d(z2)
    p3 = np.poly1d(z3)

    # Generate scatterplot with correct labels
    plt.scatter(ts, ys, label="Data points")
    plt.plot(ts, p2(ts), label="Quadratic fit", color='green', linestyle='-.')
    plt.plot(ts, p3(ts), label="Cubic fit", color='black', linestyle='-.')
    plt.ylabel("t (ms)")
    plt.xlabel("T (°C)")
    plt.ylim((0, 20))
    plt.axvline(ts[ind_fit], linestyle=':', color='red')
    plt.legend()
    plt.title("Duration of action potential for 100 temperatures between 0 and 45 "\
            "degrees Celcius with injected current of 50 $\mu$A/cm$^2$.", wrap=True)
    plt.show()

if __name__ == "__main__":
    multiple_ap_plot()
    plot_temp_exp_polyfit()
