import matplotlib.pyplot as plt
import numpy as np
import hh
import csv

class CurrentParameters:
    def __init__(self, Imean = 20, Ivar = 1, Tmean = 1, Tvar = 0.1, start_time=0):
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
        """Return a current function normaly with distributed time and strength"""
        strength = np.random.normal(self.Imean, self.Ivar)
        duration = np.random.normal(self.Tmean, self.Tvar)
        strength = max(strength, 0)
        duration = max(duration, 0)
        def I(t):
            return strength * (self.start < t < self.start + duration)
        return I


class TempExperiment:
    def __init__(self, minTemp=6.3, maxTemp=46.3, tempSteps=10, model=hh.HodgkinHuxley(), tol=10, currentPar=None):
        """Initialize values used experiment"""
        self.minTemp = minTemp
        self.maxTemp = maxTemp
        assert maxTemp > minTemp
        self.tempSteps = tempSteps
        self.model = model
        self.tol = tol
        if currentPar is None:
            self.currentPar = CurrentParameters()
        else:
            self.currentPar = currentPar

    def run(self):
        """This function runs the Hodgkin-Huxley model for different temperatures
        and measures the time it takes to finish a single action potential.
        """
        temperatures = np.linspace(self.minTemp, self.maxTemp, self.tempSteps)
        print(f"Running action potential for temperatures: {temperatures}")
        ap_durations = []
        model = self.model
        rest_pot = model.V_eq
        for T in temperatures:
            print(f"Running {T} degrees...")
            model.set_temperature(T)
            model.I = self.genCurrent()
            t, y = model.solve_model()
            volts = y[:,0]
            duration = self.determineDuration(t, volts, rest_pot)
            ap_durations.append(duration)
        assert len(temperatures) == len(ap_durations)
        self.results = (temperatures, ap_durations)

    def genCurrent(self):
        """Return current with stored paramters"""
        return self.currentPar.genCurrent()

    def determineDuration(self, t, volts, rest_pot):
        """Determine timespan during which volts is outside resting potential."""
        start_index = -1
        end_index = -1
        tol = self.tol
        assert tol > 0
        for index, v in enumerate(volts):
            # Distance from action potential
            dist = np.abs(v - rest_pot)
            if dist > tol:
                end_index = index
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
        self.tempStep = steps
        self.tol = eps
        self.model = model

    def plot(self, title="", xlabel="Temperature", ylabel="Action potential"):
        """Plots the values stored"""
        if title == "":
            title = f"AP duration vs temperature for injected current {self.currentPar.Tmean} second at {self.currentPar.Imean} volts"
        temperatures, ap_durations = self.results
        assert len(temperatures) == len(ap_durations)
        plt.plot(temperatures, ap_durations, "-o")
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()

    def store_csv(self, file_name):
        """Stores results in csv file."""
        temperatures, ap_durations = self.results
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for t, ap in zip(temperatures, ap_durations):
                writer.writerow([t, ap])

    def load_csv(self, file_name):
        """Loads results from csv file."""
        temperatures = []
        ap_durations = []
        with open(file_name, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                temperatures.append(float(row[0]))
                ap_durations.append(float(row[1]))
        self.results = (temperatures, ap_durations)

if __name__ == "__main__":
    model = hh.HodgkinHuxley()
    model.quick = True
    TE = TempExperiment(model=model)
    TE.load_csv("testfile")
    TE.plot()
    plt.show()
