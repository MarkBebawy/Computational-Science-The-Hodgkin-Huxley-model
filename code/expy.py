import matplotlib.pyplot as plt
import numpy as np
import hh
import csv

class TempExperiment:
    def __init__(self, minTemp=6.3, maxTemp=46.3, tempSteps=10, timeStep=0.0001, runTime=10, tol=10, quick=False):
        """Initialize values used experiment"""
        self.minTemp = minTemp
        self.maxTemp = maxTemp
        self.tempSteps = tempSteps
        self.timeStep = timeStep
        self.runTime = runTime
        self.tol = tol
        self.quick = quick
    
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
            t, y = model.solve_model(self.timeStep, self.runTime, quick=self.quick)
            volts = y[:,0]
            duration = self.determineDuration(t, volts, rest_pot)
            ap_durations.append(duration)
        self.results = (temperatures, ap_durations)
    
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
        plt.show()
    
    def store_csv(file_name):
        """Stores results in csv file."""
        #TODO finish
        pass
    
    def load_csv(file_name):
        """Loads results from csv file."""
        #TODO finish
        pass


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

