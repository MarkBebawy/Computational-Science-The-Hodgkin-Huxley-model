import matplotlib.pyplot as plt
import numpy as np
import hh

def speedTemperature(x=hh.HodgkinHuxley()):
    """This function runs the Hodgkin-Huxley model for different temperatures
    and measures the time it takes to finish a single action potential.

    Parameters:
    - eps: error marigin around -65 mV such that [-65 - eps, -65 + eps]
           is accepted as resting potential.
    """
    temperatures = np.linspace(x.min_temp, x.max_temp, x.amount_temp_range)
    print(f"Running action potential for temperatures: {temperatures}")
    ap_times = list()
    for T in temperatures:
        print(f"Running {T} degrees...")
        x.set_temperature(T)
        eps = x.rest_potential_eps
        t, y = x.solve_model()
        volts = y[:,0]
        for index, v in enumerate(volts):
            if -65 - eps < v and v < -65 + eps and t[index] > 4:
                ap_times.append(t[index])
                break
            if index == len(volts) - 1:
                print(f"WARNING: Did not find repolarisation for {T} degrees")
    return temperatures, ap_times


def plot(x, y):
    """Plot y against x."""
    plt.plot(x, y)
    plt.show()


if __name__ == "__main__":
    temperatures, ap_times = speedTemperature()
    plt.plot(temperatures, ap_times)
    plt.show()
