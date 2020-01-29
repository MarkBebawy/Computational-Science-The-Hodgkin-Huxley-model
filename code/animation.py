## Class Animation for running an animation of an action potential.

import matplotlib.pyplot as plt
import numpy as np
import hh
from matplotlib.animation import FuncAnimation

class Animation:
    """Class used for matplotlib animation.
    Must be provided an array of tuples (x_i,y_i). At a frame i, list y_i is plotted
    against list x_i."""
    def __init__(self, frames, xlim=(-1,1), ylim = (-1,1), frame_delay=200):
        """Creates animation object.
        Parameters:
        - frames:
            array with tuples (x,y) where y will be plotted against x.
        - (x/y)lim:
            Axis ranges for plotting. Should be (start, end).
        - frame_delay:
            Time between plots"""
        # Assert frame tuples have same length.
        for (x, y) in frames:
            assert len(x) == len(y)

        self.frames = frames
        self.frame_delay = frame_delay
        self.xlim = xlim
        self.ylim = ylim

    def start(self):
        """Function that start the animation."""
        fig, ax = plt.subplots()
        ax.set_xlim(self.xlim)
        ax.set_ylim(self.ylim)

        # Generate empty line object needed in frame_function
        self.ln, = ax.plot([],[])

        # Frame range is a list of integers as they will be used to index.
        frame_range = np.arange(len(self.frames))

        animation = FuncAnimation(fig, func=self.frame_function, frames=frame_range,
                                interval=self.frame_delay, repeat=False, blit=True)
        plt.show()

    def frame_function(self, i):
        """Function used in FuncAnimation.
        Returns tuple with line to be plotted."""
        x_data, y_data = self.frames[i]
        self.ln.set_xdata(x_data)
        self.ln.set_ydata(y_data)
        return self.ln,

if __name__ == "__main__":
    # Plot hodgkin huxley model
    neuron = hh.HodgkinHuxley()
    neuron.quick=True
    neuron.run_time = 20
    neuron.num_method_time_steps = 0.025

    # Retrieve data to be plotted.
    t, y = neuron.solve_model()
    volts = y[:,0]
    frames = [(t[:n],volts[:n]) for n in range(len(volts))]

    # Set plottting limits
    y_scaling = 1.2
    xlim = (t[0],t[-1])
    ylim = (y_scaling*min(volts),y_scaling*max(volts))

    # Start animation
    Ani = Animation(frames=frames, frame_delay=10, xlim = xlim, ylim = ylim)
    Ani.start()
