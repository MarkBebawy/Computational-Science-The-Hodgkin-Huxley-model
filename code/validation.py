import matplotlib.pyplot as plt
import numpy as np
import hh
import csv

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
        model = self.model
        maxima = []
        for inj_voltage in self.current_range:
            model.set_injection_data(inj_voltage, 0, self.current_duration)
            t, y = model.solve_model()
            cell_voltage = y[:,0]
            max_voltage = max(cell_voltage)
            maxima.append(max_voltage)
        self.maxima = maxima

    def plot(self, title="", xlabel="Injected current", ylabel="voltage peak"):
        """Plots the values stored"""
        if title == "":
            title = f"voltage peak for injected current {self.current_duration} vs injected current strength"
        maxima = self.maxima
        current_range = self.current_range
        assert len(maxima) == len(current_range)
        plt.plot(current_range, maxima, "o")
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
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
        with open(file_name, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                current_range.append(float(row[0]))
                maxima.append(float(row[1]))
        self.maxima = maxima
        self.current_range = current_range
    
if __name__ == "__main__":
    model = hh.HodgkinHuxley()
    model.quick=True
    VE = ValidationExperiment(model=model)
    #VE.run()
    VE.load_csv("testval")
    VE.plot()