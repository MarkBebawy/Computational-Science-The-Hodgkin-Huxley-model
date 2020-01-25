import numpy as np
import matplotlib.pyplot as plt
import tools

class HodgkinHuxley:
    """
    Class which stores parameters of HH model.

    Attributes:
    C_m: Membrane capacitance (uF/cm^2)
    V_eq: Equilibrium potential (mV)
    V0: Applied voltage at starting time (mV)
    n0: Initial probability of K gate being open
    m0: Initial probability of Na gate being open
    h0: Initial probability of Na gate being inactivated
    V_Na, v_K, v_L: Reverse potential of Na / K / leakage channel (mV)
    g_Na, g_K, g_L: Maximum Na / K / leakage conductance (mS/cm^2)
    a: diameter of fibre (10^-3 cm)
    R_m: Membrane resting resistance (10^3 Ohm cm^2)
    R_c: axoplasm resistivity (Ohm cm)

    phi: Factor for temperature correction
    a_n, a_m, a_h: Opening rate of m, n, h gates (ms)^-1
    b_n, b_m, b_h: Closing rate om m, n, h gates (ms)^-1
    """
    def __init__(self, T=6.3):
        """Initialises variables of model, takes temperature as input with T = 6.3 as standard temperature."""
        self.C_m = 1
        self.V_eq = -65
        self.n0 = 0.317
        self.m0 = 0.05
        self.h0 = 0.6
        self.V0 = -0.1 # Small negative displacement is needed for dynamic model
        self.V_Na =  50 - self.V_eq
        self.V_K = -77 - self.V_eq
        self.V_L = -54.4 - self.V_eq
        self.g_Na = 120
        self.g_K = 36
        self.g_L = 0.3
        self.a = 25 # 23.8 original HH article, 25 according to book
        self.R_m = 1
        self.R_c = 30 # 35.4 original HH article, 30 book

        # Space constant (cm^2) and time constant (ms).
        self.spc = self.R_m * self.a / (2 * self.R_c)
        self.tc = self.R_m * self.C_m

        # Calculate factor for temperature correction which is used for opening and closing rates.
        self.phi = 3 ** ((T - 6.3) / 10)
        self.a_n = lambda V : self.phi * (0.01 * (10 - V) / (np.exp((10 - V)/10) - 1))
        self.a_m = lambda V : self.phi * (0.1 * (25 - V) / (np.exp((25 - V)/10) - 1))
        self.a_h = lambda V : self.phi * 0.07 * np.exp(-V/20)
        self.b_n = lambda V : self.phi * 0.125 * np.exp(-V/80)
        self.b_m = lambda V : self.phi * 4 * np.exp(-V/18)
        self.b_h = lambda V : self.phi / (np.exp((30 - V)/10) + 1)

        # Ionic current functions
        self.I_L = lambda V : self.g_L * (V - self.V_L)
        self.I_K = lambda V, n :  self.g_K * n ** 4 * (V - self.V_K)
        self.I_Na = lambda V, m, h : self.g_Na * m ** 3 * h * (V - self.V_Na)
        self.I_ion = lambda V, n, m, h : self.I_K(V, n) + self.I_Na(V, m, h) + self.I_L(V)

    def I(self, t):
        """Injected current as a function of time in uA/cm^2. """
        return 20 * (3 < t < 4)


    def diff_eq(self):
        """Returns function f such that the differential equations can be described as x' = f(t, x),
        where x = [V, n, m, h]."""
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
        """Returns function f such that the differential equations can be described as x' = f(t, x),
        where x = [V, W, n, m, h]. W is a substitution variable for dV/dt. """
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

    def solve_model(self, h, t, quick=False):
        """Solves the model using RK4 with step size h, for time (at least) t. 
        If quick parameter is true then forward Euler is used."""
        N = np.int(np.ceil(t/h))
        f = self.diff_eq()
        y0 = np.array([0, self.n0, self.m0, self.h0])
        if quick:
            sol = tools.fe(f, 0, y0, h, N)
        else:
            sol = tools.rk4(f, 0, y0, h, N)
        return sol
    
    def solve_dynamic_model(self, h, t, c, quick=False):
        """Solves dynamic model using RK4 with step size h, for time (at least) t.
        If quick parameter is true then forward Euler is used.
        K is a guess for the constant K from which the propagation speed can be determined."""
        # Determine good guess for (dV/dt) at t=0. mu is the positive solution of the equation
        # mu^2 - K mu - K g_0 / C_m = 0. 
        mu, _ = tools.solve_quadratic(self.spc / c ** 2, - self.tc, -1)

        N = np.int(np.ceil(t/h))
        f = self.diff_eq_dynamic(c)
        y0 = np.array([self.V0, mu * self.V0, self.n0, self.m0, self.h0])
        if quick:
            sol = tools.fe(f, 0, y0, h, N)
        else:
            sol = tools.rk4(f, 0, y0, h, N)
        return sol
    
    def find_speed(self, c_low, c_high, h, t, n, quick=False):
        """Finds propagation speed by calculating solution for guesses of c
        and then using bisection.
        NB Unit of c is cm/ms or dam/s. 
        """
        def g(c):
            # Will most likely have NaN values due to overflow, want to find 
            # last non-NaN value. 
            _, y = self.solve_dynamic_model(h, t, c, quick)
            i = 1
            while np.isnan(y[-i, 0]):
                i += 1
            return y[-i, 0]

        return tools.bisect(g, c_low, c_high, n)
