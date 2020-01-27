## Class HodgkinHuxley implementing functions for setting all variables,
## and for creating, solving and plotting the corresponding
## differential equation (of the Hodgkin-Huxley model).

import numpy as np
import matplotlib.pyplot as plt
import tools

class HodgkinHuxley:
    """
    Class which stores parameters of HH model. The HH model describes membrane voltage within a neuron during an 
    action potential and propagation of an action potential - in this case in the squid giant axon.
    The used default values are taken from the book Mathematical Physiology by Keener and Sneyd (2nd edition). 
    All voltages (apart from V_eq) denote deviation from resting potential. 

    Attributes:
        *Biological constants and functions*
        C_m: Membrane capacitance (uF/cm^2)
        V_eq: Equilibrium potential (mV)
        V0: Voltage at starting time for dynamic model (mV)
        n0: Initial probability of K gate being open
        m0: Initial probability of Na gate being open
        h0: Initial probability of Na gate being inactivated
        V_Na, v_K, v_L: Reverse potential of Na / K / leakage channel (mV)
        g_Na, g_K, g_L: Maximum Na / K / leakage conductance (mS/cm^2)
        a: Diameter of fibre (10^-3 cm)
        R_m: Membrane resting resistivity (10^3 Ohm cm^2)
        R_c: axoplasm resistivity (Ohm cm)
        spc: Squared membrane space constant (cm^2), given by spc = R_m * a / (2 * R_c)
        tc: Membrane time constant (ms), given by tc = C_m * R_m
        I_L, I_K, I_na: Current density Na / K / leakage channel (uA/cm^2)
        I_ion: Total ionic current (sum of I_L, I_K, I_Na) (uA/cm^2)

        *Functions which depend on temperature* 
        T: Temperature in degrees Celcius
        phi: Factor for temperature correction
        a_n, a_m, a_h: Opening rate of m, n, h gates (kHz)
        b_n, b_m, b_h: Closing rate om m, n, h gates (kHz)

        *Constants for modelling*
        run_time: amount of seconds simulated in model (ms)
        quick: determines whether FE (True) or RK4 (False) is used for solving differential equations
        num_method_time_steps: size of time steps for FE/RK4 (ms)
        inject_current: amount of injected current (uA/cm^2)
        inj_start_time, inj_end_time: starting / ending time of current injection (ms) 
        results: tuple where first element is list of times and second is array of voltage data. 
    """
    def __init__(self, T=6.3):
        """Initialises variables of model corresponding to the given temperature."""
        # Biological constants
        self.C_m = 1
        self.V_eq = -65
        self.V0 = -0.1
        self.n0 = 0.317
        self.m0 = 0.05
        self.h0 = 0.6
        self.V_Na =  50 - self.V_eq
        self.V_K = -77 - self.V_eq
        self.V_L = -54.4 - self.V_eq
        self.g_Na = 120
        self.g_K = 36
        self.g_L = 0.3
        self.a = 25
        self.R_m = 1
        self.R_c = 30
        self.spc = self.R_m * self.a / (2 * self.R_c)
        self.tc = self.R_m * self.C_m
        self.I_L = lambda V : self.g_L * (V - self.V_L)
        self.I_K = lambda V, n :  self.g_K * n ** 4 * (V - self.V_K)
        self.I_Na = lambda V, m, h : self.g_Na * m ** 3 * h * (V - self.V_Na)
        self.I_ion = lambda V, n, m, h : self.I_K(V, n) + self.I_Na(V, m, h) + self.I_L(V)

        # Set parameters that can be changed by GUI.
        self.run_time = 10
        self.quick = False
        self.num_method_time_steps = 0.0001

        # Set parameters that can be changed by GUI and are meant for simulating
        # one action potential.
        self.set_temperature(T)
        self.inject_current = 20
        self.inj_start_time = 3
        self.inj_end_time = 4

        # Results, to be plotted...
        self.results = ([], [])

    def set_temperature(self, T):
        """Setter for the temperature of the model."""
        self.temperature = T
        self.phi = 3 ** ((T - 6.3) / 10)
        self.a_n = lambda V : self.phi * (0.01 * (10 - V) / (np.exp((10 - V)/10) - 1))
        self.a_m = lambda V : self.phi * (0.1 * (25 - V) / (np.exp((25 - V)/10) - 1))
        self.a_h = lambda V : self.phi * 0.07 * np.exp(-V/20)
        self.b_n = lambda V : self.phi * 0.125 * np.exp(-V/80)
        self.b_m = lambda V : self.phi * 4 * np.exp(-V/18)
        self.b_h = lambda V : self.phi / (np.exp((30 - V)/10) + 1)


    def update_parameters(self):
        """Updates parameters dependent on other parameters."""
        self.set_temperature(self.temperature)
        self.I_L = lambda V : self.g_L * (V - self.V_L)
        self.I_K = lambda V, n :  self.g_K * n ** 4 * (V - self.V_K)
        self.I_Na = lambda V, m, h : self.g_Na * m ** 3 * h * (V - self.V_Na)
        self.I_ion = lambda V, n, m, h : self.I_K(V, n) + self.I_Na(V, m, h) + self.I_L(V)
    
    def I(self, t):
        """Injects a current of inject_current uA/cm^2 between inj_start_time and inj_end_time. """
        return self.inject_current * (self.inj_start_time < t < self.inj_end_time)

    def diff_eq(self):
        """Returns function f such that the differential equations for the basic hodgkin-huxley model can be 
        described as x' = f(t, x), where x = [V, n, m, h]."""
        def f(t, x):
            V, n, m, h = x
            y = np.zeros(4)
            y[0] = (self.I(t) - self.I_ion(V, n, m, h)) / self.C_m
            y[1] = self.a_n(V) * (1 - n) - self.b_n(V) * n
            y[2] = self.a_m(V) * (1 - m) - self.b_m(V) * m
            y[3] = self.a_h(V) * (1 - h) - self.b_h(V) * h
            return y
        return f

    def diff_eq_dynamic(self, c):
        """Returns function f such that the differential equations for HH with propagation can be described as 
        x' = f(t, x), where x = [V, W, n, m, h]. Here, W is a substitution variable for dV/dt. The parameter c 
        is the propagation speed in cm/ms."""
        def f(t, x):
            V, W, n, m, h = x
            y = np.zeros(5)
            y[0] = W
            y[1] = (c ** 2 / self.spc) * (self.tc * W + self.R_m * self.I_ion(V, n, m, h))
            y[2] = self.a_n(V) * (1 - n) - self.b_n(V) * n
            y[3] = self.a_m(V) * (1 - m) - self.b_m(V) * m
            y[4] = self.a_h(V) * (1 - h) - self.b_h(V) * h
            return y
        return f


    def set_run_time(self, time):
        """Setter for the run time of the model."""
        self.run_time = time

    def set_injection_data(self, inj_current, inj_start, inj_end):
        """Setter for inject_current, inj_start_time, inj_end_time."""
        self.inject_current = inj_current
        self.inj_start_time = inj_start
        self.inj_end_time = inj_end

    def set_num_method(self, quick, steps):
        """Setter for numerical method (quick=False --> RK4, quick=True --> Forward Euler)
        and for time steps used by that method."""
        self.quick = quick
        self.num_method_time_steps = steps

    def solve_model(self, h=None, t=None, quick=None):
        """Solves the model using FE/RK4 with step size h, for time (at least) t.
        Starting voltage is 0."""
        # Default values for parameters.
        if h is None:
            h = self.num_method_time_steps
        if t is None:
            t = self.run_time
        if quick is None:
            quick = self.quick

        # Calculate number of steps, differential equation and solve it.
        N = np.int(np.ceil(t/h))
        f = self.diff_eq()
        y0 = np.array([0, self.n0, self.m0, self.h0])
        if quick:
            sol = tools.fe(f, 0, y0, h, N)
        else:
            sol = tools.rk4(f, 0, y0, h, N)

        self.results = sol
        return sol
    
    def run_multiple_ap(self, temps):
        """TODO documentatie :))"""
        N = np.int(np.ceil(self.run_time/self.num_method_time_steps))
        num = len(temps)
        t = np.array([i * self.num_method_time_steps for i in range(N+1)])
        ys = np.zeros((num, N+1))
        for i, T in enumerate(temps):
            self.set_temperature(T)
            ts, y = self.solve_model()
            ys[i] = y[:,0]
        return t, ys
    
    def plot_multiple_ap(self, temps):
        # TODO: use coolwarm diverging colormap
        t, ys = self.run_multiple_ap(temps)
        for i, y in enumerate(ys):
            plt.plot(t, y, label=f"{temps[i]} degrees")
        plt.legend()
        plt.title("TODO titel")
        plt.xlabel("Temperature (degrees celsius)")
        plt.ylabel("Voltage (mV)")
        plt.show()

    def solve_dynamic_model(self, h, t, c, quick=False):
        """Solves dynamic model using FE/RK4 with step size h, for time (at least) t.
        The parameter c is the propagation speed in cm/ms.
        
        First determines a guess for dV/dt at t=0, which is V0 * mu where mu is the positive
        solution of the quadratic equation spc/c^2 * mu^2 - self.tc * mu - 1 = 0. 
        """
        # Determine good guess for W = dV/dt at t=0. mu is the positive solution of the 
        # quadratic equation 
        mu, _ = tools.solve_quadratic(self.spc / c ** 2, - self.tc, -1)

        N = np.int(np.ceil(t/h))
        f = self.diff_eq_dynamic(c)
        y0 = np.array([self.V0, mu * self.V0, self.n0, self.m0, self.h0])
        if quick:
            sol = tools.fe(f, 0, y0, h, N)
        else:
            sol = tools.rk4(f, 0, y0, h, N)

        self.results = sol
        return sol
    
    def find_speed(self, c_low, c_high, h, t, n, quick=False):
        """Finds propagation speed by calculating solution for guesses of c. Theoretically, if c was guessed too low
        the voltage should diverge to +∞, while is c was guessed to high the voltage should diverge to -∞. Therefore, 
        using bisection we should be able to find the value of c for which the voltage returns to resting potential,
        which is the propagation speed. The unit of c is cm/ms.

        To this end, we define the function g of c which simulates the model using c as a guess for the propagation speed,
        and returns the last membrane voltage before overflow occurs. We then use bisection on this function g.
        """
        def g(c):
            _, y = self.solve_dynamic_model(h, t, c, quick)
            i = 1
            while np.isnan(y[-i, 0]):
                i += 1
            return y[-i, 0]
        return tools.bisect(g, c_low, c_high, n)

    def plot_results(self):
        """This function plots the results of an action potential plot."""
        t, y = self.results
        assert len(t) == len(y[:,0])
        title = (f"One neuron action potential. Voltage plotted against "
        f"time, using temperature {self.temperature} degrees, "
        f"injecting {self.inject_current} mV current "
        f"from {self.inj_start_time} ms to {self.inj_end_time} ms. "
        f"Numerical method {'Runge-Kutta-4' if self.quick == 0 else 'Forward-Euler'} "
        f"with time steps {self.num_method_time_steps}.")

        plt.title(title, wrap=True)
        plt.xlabel("Time (ms)")
        plt.ylabel("Voltage (mV)")
        plt.plot(t, y[:,0], c='red')
        plt.show()

if __name__ == "__main__":
    x = HodgkinHuxley()
    temps = [-15, -10, -5, 0, 5, 10, 15, 20, 25]
    x.plot_multiple_ap(temps)
