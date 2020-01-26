## TempExperiment class for running temperature experiments, using
## current injection parameters from CurrentParameters class.

import matplotlib.pyplot as plt
import numpy as np
import hh
import csv
import os

class CurrentParameters:
    def __init__(self, Imean = 20, Ivar = 3, Tmean = 1, Tvar = 0.5, start_time=0):
        """Store current paramters in object.
        Parameters:
        - Imean: mean current strength,
        - Ivar: variance of current strength,
        - Tmean: mean time,
        - Tvar: time variance
        """
        self.Imean = Imean
        self.Ivar = Ivar
        self.Tmean = Tmean
        self.Tvar = Tvar
        self.start_time = start_time

    def genCurrent(self):
        """Return a current function with normally distributed time and strength."""
        strength = np.random.normal(self.Imean, self.Ivar)
        duration = np.random.normal(self.Tmean, self.Tvar)
        strength = max(strength, 0)
        duration = max(duration, 0)
        def I(t):
            return strength*(self.start_time < t and t < self.start_time + duration)
        return I

    def set_curr_data(self, Imean, Ivar, Tmean, Tvar, start):
        """Setter for all instance variables."""
        self.Imean = Imean
        self.Ivar = Ivar
        self.Tmean = Tmean
        self.Tvar = Tvar
        self.start_time = start


class TempExperiment:
    def __init__(self, minTemp=6.3, maxTemp=46.3, tempSteps=10, model=hh.HodgkinHuxley(), tol=0.5, currentPar=None):
        """Initialize values used experiment.
        Parameters:
        - minTemp, maxTemp, tempsteps:
            Used for temperature range in which to test.
        - model:
            model of neuron
        - tol:
            tolerance used to distinguish from resting potential.
            We consider the range [-tol, +tol] to be resting potential
        - currentPar:
            class containing current injection parameters."""
        self.minTemp = minTemp
        self.maxTemp = maxTemp
        self.tempSteps = tempSteps
        self.model = model
        self.tol = tol

        if currentPar is None:
            self.currentPar = CurrentParameters()
        else:
            self.currentPar = currentPar

    def run(self, num_expr=3):
        """This function runs the Hodgkin-Huxley model for different temperatures
        and measures the time it takes to finish a single action potential."""
        temperatures = np.linspace(self.minTemp, self.maxTemp, self.tempSteps)
        print(f"Running action potential for temperatures: {temperatures}")

        # durations_list should be a 2d array with multiple values for each temperature.
        durations_list = []
        model = self.model
        rest_pot = model.V_eq

        # Determine AP duration for each temperature
        for T in temperatures:
            print(f"Running {T} degrees...")
            model.set_temperature(T)
            durations = []

            # Run each temperature multiple times, for statistical confidence.
            for i in range(num_expr):
                model.I = self.genCurrent()
                t, y = model.solve_model()
                volts = y[:,0]
                duration = self.determineDuration(t, volts, rest_pot)
                durations.append(duration)
            durations_list.append(durations)

        assert len(temperatures) == len(durations_list)
        self.results = (temperatures, durations_list)
        return self.results

    def genCurrent(self):
        """Return current with stored paramters"""
        return self.currentPar.genCurrent()

    def determineDuration(self, t, volts, V_eq):
        """Determine timespan during which volts is outside resting potential.
        We look for the difference between first and last time the voltage is in resting potential.
        Resting potential is defined as [V_eq - tol, V_eq + tol].
        The tolerance is stored in the experiment class."""
        assert len(volts) == len(t)
        start_index = -1
        end_index = -1
        tol = self.tol
        assert tol > 0

        for index, v in enumerate(volts):
            # Distance from action potential, end_index is increased until
            # returning to resting potential and not leaving resting potential
            # for the rest of the running time.
            dist = np.abs(v)
            if dist > tol:
                end_index = index

                # If this time step is the first time outside resting potential,
                # then action potential is starting now.
                if start_index == -1:
                    start_index = index

        # If end_index is still -1, no action potential was reached.
        if end_index == -1:
            return 0
        else:
            return t[end_index] - t[start_index]

    def set_temp_exp_data(self, min_temp, max_temp, steps, eps, model):
        """This function sets the temperature experiment variables."""
        self.minTemp = min_temp
        self.maxTemp = max_temp
        self.tempSteps = steps
        self.tol = eps
        self.model = model

    def plot(self, title="", xlabel="Temperature (degrees celsius)", ylabel="Action potential duration (ms)"):
        """Plots the values stored: duration of action potential against
        temperature."""
        if title == "":
            title = (f"Duration of action potential plotted against temperature. "
                     f"Injected normal distributed current with mean of {self.currentPar.Imean} mV "
                     f"for normal distributed duration with mean {self.currentPar.Tmean} ms. Standard deviations "
                     f"{self.currentPar.Ivar} and {self.currentPar.Tvar} respectively.")

        # Retrieve results
        temperatures, durations_list = self.results
        assert len(temperatures) == len(durations_list)

        # Format results for plt.scatter
        x = []
        y = []
        for durations, temp in zip(durations_list, temperatures):
            for duration in durations:
                x.append(temp)
                y.append(duration)

        plt.title(title, wrap=True)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.scatter(x, y)
        plt.show()

    def store_csv(self, file_name):
        """Stores results in csv file."""
        temperatures, durations_list = self.results
        assert len(temperatures) == len(durations_list)
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for t, ap in zip(temperatures, durations_list):
                writer.writerow([t, *ap])

    def load_csv(self, file_name):
        """Loads results from csv file."""
        assert os.path.isfile(file_name)

        temperatures = []
        durations_list = []
        with open(file_name, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                temperatures.append(float(row[0]))
                durations = list(map(float, row[1:]))
                durations_list.append(durations)

        assert len(temperatures) == len(durations_list)
        self.results = (temperatures, durations_list)
