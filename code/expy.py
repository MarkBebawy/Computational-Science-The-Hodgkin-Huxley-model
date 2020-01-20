import matplotlib.pyplot as plt
import numpy as np
import hh
import csv

# def speedTemperature(x=hh.HodgkinHuxley()):
#     """This function runs the Hodgkin-Huxley model for different temperatures
#     and measures the time it takes to finish a single action potential.

#     Parameters:
#     - eps: error marigin around -65 mV such that [-65 - eps, -65 + eps]
#            is accepted as resting potential.
#     """
#     temperatures = np.linspace(x.min_temp, x.max_temp, x.amount_temp_range)
#     print(f"Running action potential for temperatures: {temperatures}")
#     ap_times = list()
#     for T in temperatures:
#         print(f"Running {T} degrees...")
#         x.set_temperature(T)
#         eps = x.rest_potential_eps
#         t, y = x.solve_model()
#         volts = y[:,0]
#         for index, v in enumerate(volts):
#             if -65 - eps < v and v < -65 + eps and t[index] > 4:
#                 ap_times.append(t[index])
#                 break
#             if index == len(volts) - 1:
#                 print(f"WARNING: Did not find repolarisation for {T} degrees")
#     return temperatures, ap_times


# def plot(x, y):
#     """Plot y against x."""
#     plt.plot(x, y)
#     plt.show()


# if __name__ == "__main__":
#     temperatures, ap_times = speedTemperature()
#     plt.plot(temperatures, ap_times)
#     plt.show()

class CurrentParamters:
    def __init__(self, Imean = 20, Ivar = 1, Tmean = 1, Tvar = 0.1):
        """Store current paramters in object.
        Parameters:
        - Imean: mean current strength,
        - Ivar: variance of current strength,
        - Tmean: mean time,
        - Tvar: mean variance
        """
        self.Imean = Imean
        self.Ivar = Ivar
        self.Tmean = Tmean
        self.Tvar = Tvar

    def genCurrent(self):
        """Return a current function normaly with distributed time and strength"""
        #TODO: could give negative duration/strength
        strength = np.random.normal(self.Imean, self.Ivar)
        duration = np.random.normal(self.Tmean, self.Tvar)
        strength = max(strength, 0)
        duration = max(duration, 0)
        def I(t):
            return strength*(t < duration)
        return I



class TempExperiment:
    def __init__(self, minTemp=6.3, maxTemp=46.3, tempSteps=10, timeStep=0.0001, runTime=10, tol=10, quick=False, currentPar = None):
        """Initialize values used experiment"""
        self.minTemp = minTemp
        self.maxTemp = maxTemp
        self.tempSteps = tempSteps
        self.timeStep = timeStep
        self.runTime = runTime
        self.tol = tol
        self.quick = quick
        if currentPar is None:
            self.currentPar = CurrentParamters()
        else:
            self.currentPar = currentPar

    def run(self):
        """This function runs the Hodgkin-Huxley model for different temperatures
        and measures the time it takes to finish a single action potential.

        Parameters:
        - eps: error marigin around -65 mV such that [-65 - eps, -65 + eps]
        is accepted as resting potential.
        """
        temperatures = np.linspace(self.minTemp, self.maxTemp, self.tempSteps)
        ap_durations = []
        for T in temperatures:
            model = hh.HodgkinHuxley(T=T)
            rest_pot = model.V_eq
            model.I = self.genCurrent()
            t, y = model.solve_model(self.timeStep, self.runTime, quick=self.quick)
            volts = y[:,0]
            duration = self.determineDuration(t, volts, rest_pot)
            ap_durations.append(duration)
        self.results = (temperatures, ap_durations)

    def genCurrent(self):
        """return current with stored paramters"""
        return self.currentPar.genCurrent()

    def determineDuration(self, t, volts, rest_pot):
        """Determine timespan during which volts is outside resting potential."""
        start_index = -1
        end_index = -1
        tol = self.tol
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

    def plot(self, title="Action potential duration vs temperature", xlabel="Temperature", ylabel="Action potential"):
        """Plots the values stored"""
        temperatures, ap_durations = self.results
        plt.plot(temperatures, ap_durations)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.figtext(0.99, 0.5, 'footnote text \n test \n test', horizontalalignment='right')
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

TE = TempExperiment(quick=True)
TE.run()
TE.plot()
plt.show()





# def speedTemperature(minTemp=6.3, maxTemp=46.3, tempSteps=10, rkTimeSteps=0.0001, runTime=10, eps=10):
#     """This function runs the Hodgkin-Huxley model for different temperatures
#     and measures the time it takes to finish a single action potential.

#     Parameters:
#     - eps: error marigin around -65 mV such that [-65 - eps, -65 + eps]
#            is accepted as resting potential.
#     """
#     temperatures = np.linspace(minTemp, maxTemp, tempSteps)
#     ap_times = list()
#     for T in temperatures:
#         model = hh.HodgkinHuxley(T)
#         t, y = model.solve_model(rkTimeSteps, runTime)
#         volts = y[:,0]
#         for index, v in enumerate(volts):
#             if -65 - eps < v and v < -65 + eps and t[index] > 4:
#                 ap_times.append(t[index])
#                 break
#     return temperatures, ap_times

