import matplotlib.pyplot as plt
import numpy as np
import hh

def speedTemperature(minTemp=6.3, maxTemp=46.3, tempSteps=10, rkTimeSteps=0.0001, runTime=10, eps=10):
    """This function runs the Hodgkin-Huxley model for different temperatures
    and measures the time it takes to finish a single action potential.

    Parameters:
    - eps: error marigin around -65 mV such that [-65 - eps, -65 + eps]
           is accepted as resting potential.
    """
    temperatures = np.linspace(minTemp, maxTemp, tempSteps)
    ap_times = list()
    for T in temperatures:
        model = hh.HodgkinHuxley(T)
        t, y = model.solve_model(rkTimeSteps, runTime)
        volts = y[:,0]
        for index, v in enumerate(volts):
            if -65 - eps < v and v < -65 + eps and t[index] > 4:
                ap_times.append(t[index])
                break
    return temperatures, ap_times

temperatures, ap_times = speedTemperature()
plt.plot(temperatures, ap_times)
plt.show()
