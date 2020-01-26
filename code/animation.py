import matplotlib.pyplot as plt
import numpy as np
import hh
from matplotlib.animation import FuncAnimation

class Animation:
    """Class used for matplotlib animation. 
    Must be provided an array of frames (x_i,y_i). At a frame i, x_i is plotted against y_i."""
    def __init__(self, frames, xlim=(-1,1), ylim = (-1,1), frame_delay=200):
        """Creates animation object.
        Parameters:
        - frames:
            array with tuples (x,y) where x will be plotted against y.
        - (x/y)lim:
            Axis ranges for plotting. Should be (start, end).
        - frame_delay:
            Time between plots"""
        self.frames = frames
        self.frame_delay = frame_delay
        self.xlim = xlim
        self.ylim = ylim

    def start(self):
        """Function that start the animation. """
        fig, ax = plt.subplots()
        ax.set_xlim(self.xlim)
        ax.set_ylim((self.ylim))

        # Generate empty line object needed in frame_function
        self.ln, = ax.plot([],[])

        # Frame range is a list of integers as they will be used to index.
        frame_range = np.arange(len(self.frames))

        animation = FuncAnimation(fig, func=self.frame_function, frames = frame_range, interval=self.frame_delay, repeat = False)
        plt.show()
    
    def frame_function(self, i):
        """Function used in FuncAnimation.
        Returns tuple with line to be plotted."""
        x_data, y_data = self.frames[i]
        self.ln.set_xdata(x_data)
        self.ln.set_ydata(y_data)
        return self.ln,

if __name__ == "__main__":
    # Test plotting a sinewave
    x = np.linspace(0, 4*np.pi, 1000)
    frames = []
    for mag in np.linspace(1, -1, 100):
        y = mag*np.sin(x)
        frame = (x,y)
        frames.append(frame)

    Ani = Animation(frames=frames, frame_delay=80, xlim = (0,4*np.pi))
    Ani.start()
