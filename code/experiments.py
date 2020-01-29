## ParamExperiment class for running experiments by changing
## a certain parameter, using current injection parameters
## from CurrentParameters class.

import matplotlib.pyplot as plt
import numpy as np
import hh
import csv
import os

class CurrentParameters:
    """Object to store parameters of and generate a normally distributed current function.
    This current function returns the strength from a start time for certain duration and
    returns 0 outside that interval. The current strength (I) and duration (T) are both
    normally distributed."""
    def __init__(self, Imean = 20, Ivar = 3, Tmean = 1, Tvar = 0.5, start_time=0):
        """Store current paramters in object.
        Parameters:
        - Imean: mean current strength,
        - Ivar: variance of current strength,
        - Tmean: mean injection time,
        - Tvar: time variance
        - start_time: starting injection time
        """
        self.set_curr_data(Imean, Ivar, Tmean, Tvar, start_time)

    def genCurrent(self):
        """Return a current function with normally distributed time and strength."""
        strength = np.random.normal(self.Imean, self.Ivar)
        duration = np.random.normal(self.Tmean, self.Tvar)

        # Only allow non-negative strength and duration.
        strength = max(strength, 0)
        duration = max(duration, 0)
        def I(t):
            return strength*(self.start_time < t and t < self.start_time + duration)
        return I

    def set_curr_data(self, Imean, Ivar, Tmean, Tvar, start):
        """Setter for all instance variables."""
        assert Imean >= 0
        assert Ivar >= 0
        assert Tmean >= 0
        assert Tvar >= 0
        assert start_time >= 0

        self.Imean = Imean
        self.Ivar = Ivar
        self.Tmean = Tmean
        self.Tvar = Tvar
        self.start_time = start

class ParamExperiment:
    """Experiment class that tests the effect of a given paramter on action potential duration.
        Makes use of normally distributed current."""
    def __init__(self, update_param, min_param=6.3, max_param=46.3, param_steps=10, model=hh.HodgkinHuxley(), tol=0.5, currentPar=None):
        """Initialize values used experiment.
        Parameters:
        - update_param:
            function that updates the desired paramater (takes HodgkinHuxley and param value)
        - min_param, max_param, param_steps:
            Used for parameter range in which to test.
        - model:
            model of neuron (Hodgkin Huxley)
        - tol:
            tolerance used to distinguish from resting potential.
            We consider the range [-tol, +tol] to be resting potential
        - currentPar:
            class containing current injection parameters."""
        self.min_param = min_param
        self.max_param = max_param
        self.update_param = update_param
        self.param_steps = param_steps
        self.model = model
        self.tol = tol
        self.results = ([],[])

        if currentPar is None:
            self.currentPar = CurrentParameters()
        else:
            self.currentPar = currentPar

    def run(self, num_expr=3, savefile=None):
        """This function runs the Hodgkin-Huxley model for different parameter values
        and measures the time it takes to finish a single action potential."""
        param_range = np.linspace(self.min_param, self.max_param, self.param_steps)
        print(f"Running action potential for param_range: {param_range}")

        # durations_list should be a 2d array with multiple values for each parameter.
        durations_list = []
        model = self.model
        rest_pot = model.V_eq

        # Determine AP duration for each parameter
        for val in param_range:
            print(f"Running value: {val} ...")
            self.update_param(model, val)
            durations = []

            # Run each parameter multiple times, for statistical confidence.
            for i in range(num_expr):
                model.I = self.genCurrent()
                t, y = model.solve_model()
                volts = y[:,0]
                duration = self.determineDuration(t, volts, rest_pot)
                durations.append(duration)
            durations_list.append(durations)

        assert len(param_range) == len(durations_list)
        self.results = (param_range, durations_list)
        if savefile:
            self.store_csv(savefile)
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

    def set_param_exp_data(self, min_param, max_param, steps, eps, model):
        """This function sets the parameter experiment variables."""
        self.min_param = min_param
        self.max_param = max_param
        self.param_steps = steps
        self.tol = eps
        self.model = model

    def plot(self, title="", xlabel="", ylabel="", param_name="", poly_range = []):
        """Plots the values stored: duration of action potential against
        a given parameter.
        Poly_range a list of degrees. For each one, a polynomial of that degree will be fitted through results and plotted. """
        if title == "":
            title = (f"Duration of action potential plotted against {param_name}. "
                     f"Injected normal distributed current with mean of {self.currentPar.Imean} mV "
                     f"for normal distributed duration with mean {self.currentPar.Tmean} ms. Standard deviations "
                     f"{self.currentPar.Ivar} and {self.currentPar.Tvar} respectively.")

        # Retrieve results
        param_range, durations_list = self.results
        assert len(param_range) == len(durations_list)

        # Format results for plt.scatter
        x = []
        y = []
        for durations, param_val in zip(durations_list, param_range):
            for duration in durations:
                x.append(param_val)
                y.append(duration)
        # Fit and plot polynomials
        for degree in poly_range:
            pol = self.fit_poly(degree=degree)
            pol_y = pol(np.array(x))
            plt.plot(x,pol_y, label=f"Degree: {degree}")

        plt.title(title, wrap=True)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.scatter(x, y, label="Measured data", c="black")
        plt.legend()
        plt.show()

    def store_csv(self, file_name):
        """Stores results in csv file.
        File format:
         - column 0: parameter value
         - column > 0: AP durations"""
        param_range, durations_list = self.results
        assert len(param_range) == len(durations_list)
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for val, ap in zip(param_range, durations_list):
                writer.writerow([val, *ap])

    def load_csv(self, file_name):
        """Loads results from csv file.
        File format:
         - column 0: parameter value
         - column > 0: AP durations"""
        assert os.path.isfile(file_name)

        param_range = []
        durations_list = []
        with open(file_name, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                param_range.append(float(row[0]))
                durations = list(map(float, row[1:]))
                durations_list.append(durations)

        assert len(param_range) == len(durations_list)
        self.results = (param_range, durations_list)

    def fit_poly(self, degree):
        """Fits a polynomial of a given degree through data.
        Returns polynomial object"""
        # Format results for polynomial fit
        param_range, durations_list = self.results
        x = []
        y = []
        for durations, param_val in zip(durations_list, param_range):
            for duration in durations:
                x.append(param_val)
                y.append(duration)
        return np.polynomial.Polynomial.fit(x,y,degree)

    def fit_degree(self):
        """Fits formula of form y = c*x^n.
        All values must be greater than 0 or None will be returned."""
        # Format results for polynomial fit
        param_range, durations_list = self.results
        x = []
        y = []
        for durations, param_val in zip(durations_list, param_range):
            for duration in durations:
                x.append(param_val)
                y.append(duration)

        # Take log and return if 0
        if 0 in x or 0 in y:
            return 0,0
        x = np.array(x)
        y = np.array(y)
        lx = np.log(x)
        ly = np.log(y)

        # By assumption log(y) = n log(x) + log(c)
        coefs = np.polyfit(x,y,1)

        # Return n, c
        return coefs[0], np.exp(coefs[1])


class TempExperiment(ParamExperiment):
    """Class for an experiment measuring the effect of Temperature of action potential duration.
    Uses Hodgekin Huxely model of a neuron and measures a single action potential at a time.
    Has file management functions and a plot function."""
    def __init__(self, min_temp=6.3, max_temp=46.3, temp_steps=10, model=hh.HodgkinHuxley(), tol=0.5, currentPar=None):
        """Initialize values used experiment.
        Parameters:
        - minTemp, maxTemp, tempsteps:
            Used for temperature range in which to test.
        - model:
            model of neuron (HodgkinHuxley object)
        - tol:
            tolerance used to distinguish from resting potential.
            Given equilibrium optential Ve, we consider the range [V - tol, V + tol] to be resting potential
        - currentPar:
            object containing current injection parameters."""
        def update_func(neuron, value):
            neuron.set_temperature(value)
        super().__init__(update_func, min_param=min_temp, max_param=max_temp, param_steps=temp_steps, \
            model=model, tol=tol, currentPar=currentPar)

    def set_temp_exp_data(self, min_temp, max_temp, steps, eps, model, curr_params):
        """This function sets/updates the temperature experiment variables."""
        self.min_param = min_temp
        self.max_param = max_temp
        self.param_steps = steps
        self.tol = eps
        self.model = model
        self.currentPar = curr_params

    def plot(self, title="", xlabel="Temperature (degrees celsius)", ylabel="Action potential duration (ms)", poly_range=[]):
        """Plots the values stored: duration of action potential against
        temperature.
        Poly_range a list of degrees. For each one, a polynomial of that degree will be fitted through results and plotted. """
        if title == "":
            title = (f"Duration of action potential plotted against temperature. "
                     f"Injected normal distributed current with mean of {self.currentPar.Imean} mV "
                     f"for normal distributed duration with mean {self.currentPar.Tmean} ms. Standard deviations "
                     f"{self.currentPar.Ivar} and {self.currentPar.Tvar} respectively.")

        super().plot( title=title, xlabel=xlabel, ylabel=ylabel, poly_range=poly_range)
