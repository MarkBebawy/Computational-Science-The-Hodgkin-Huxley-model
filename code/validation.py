## Class ValidationExperiment: for experiment verification, by showing
## that our model obeys the all-or-nothing principle: amount of injected
## current only affects if there is an action potential or not.
## Injecting current above a certain threshold starts an action potential,
## for which the voltage peak stays constant when injecting more current.

import matplotlib.pyplot as plt
import numpy as np
import hh
import csv
import os

class ValidationExperiment:
    def __init__(self, current_duration=0.5, current_range=np.linspace(0,60,15), model=hh.HodgkinHuxley()):
        """Initialize validation experiment.
        Paramters:
        - current_duration:
            time for which current will be injected
        - current_range:
            range of rates at which current is injected. Should be lower than the peak value.
        - model:
            Hodgkin Huxley model of a neuron.
            Contains time and number of steps used in the numerical method (and which to use)."""
        self.current_duration = current_duration
        self.current_range = current_range
        self.model = model

    def run(self):
        """Runs the validation experiment."""
        print(f"Injecting currents: {self.current_range}")
        model = self.model
        maxima = []

        # For each voltage, solve model and append peak voltage to maxima.
        for inj_voltage in self.current_range:
            print(f"Injecting {inj_voltage}...")
            model.set_injection_data(inj_voltage, 0, self.current_duration)

            t, y = model.solve_model()
            cell_voltage = y[:,0]
            max_voltage = max(cell_voltage)
            maxima.append(max_voltage)

        self.maxima = maxima
        return maxima

    def plot(self, title="", xlabel="Injected current (mV)", ylabel="Voltage peak (mV)"):
        """Plots the values stored: voltage peak against injected current strength."""
        if title == "":
            title = (f"Voltage peak (with injecting current for {self.current_duration} ms) "
                      "plotted against injected current strength")
        maxima = self.maxima
        current_range = self.current_range
        assert len(maxima) == len(current_range)

        plt.title(title, wrap=True)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        # Make positive points green.
        cutoff = 40
        colorvec = ['green' if val > cutoff else 'red' for val in maxima]
        plt.scatter(current_range, maxima, c=colorvec)
        plt.show()

    def store_csv(self, file_name):
        """Stores results in csv file."""
        maxima = self.maxima
        current_range = self.current_range
        assert len(current_range) == len(maxima)

        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for c, m  in zip(current_range, maxima):
                writer.writerow([c, m])

    def load_csv(self, file_name):
        """Loads results from csv file."""
        current_range = []
        maxima = []

        assert os.path.isfile(file_name)
        with open(file_name, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                current_range.append(float(row[0]))
                maxima.append(float(row[1]))

        assert len(maxima) == len(current_range)
        self.maxima = maxima
        self.current_range = current_range
