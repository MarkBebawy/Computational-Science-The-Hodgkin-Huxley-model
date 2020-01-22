import numpy as np
import matplotlib.pyplot as plt
import tools

class HodgkinHuxley:
    """
    Class which stores parameters of HH model.

    Attributes:
    C: Membrane capacitance (uF/cm^2)
    I: Applied current, assumed constant (nA)
    V0: Applied voltage at starting time (mV)
    n0: Initial probability of K gate being open
    m0: Initial probability of Na gate being open
    h0: Initial probability of Na gate being inactivated
    V_Na, v_K, v_L: Reverse potential of Na / K / leakage channel (mV)
    g_Na, g_K, g_L: Maximum Na / K / leakage conductance (mS/cm^2)
    a: diameter of fibre (um)
    R: axoplasm resistivity (Ohm cm)

    phi: Factor for temperature correction
    a_n, a_m, a_h: Opening rate of m, n, h gates (ms)^-1
    b_n, b_m, b_h: Closing rate om m, n, h gates (ms)^-1
    """
    def __init__(self, T=6.3):
        """Initialises variables of model, takes temperature as input with T = 6.3 as standard temperature."""
        self.C = 1
        self.V_eq = -65
        self.n0 = 0.317
        self.m0 = 0.05
        self.h0 = 0.6
        self.V0 = -0.1 # Small negative displacement is needed for dynamic model
        self.V_Na = 50 - self.V_eq
        self.V_K = -77 - self.V_eq
        self.V_L = -54.4 - self.V_eq
        self.g_Na = 120
        self.g_K = 36
        self.g_L = 0.3
        self.a = 0.0238 # 238 original HH article, 476 according to other article
        self.R = 35.4

        # Calculate factor for temperature correction which is used for opening and closing rates.
        self.phi = 3 ** ((T - 6.3) / 10)
        self.a_n = lambda V : self.phi * (0.01 * (-V + 10) / (np.exp((-V  + 10)/10) - 1))
        self.a_m = lambda V : self.phi * (0.1 * (-V  + 25) / (np.exp((-V + 25)/10) - 1))
        self.a_h = lambda V : self.phi * 0.07 * np.exp(-V/20)
        self.b_n = lambda V : self.phi * 0.125 * np.exp(-V/80)
        self.b_m = lambda V : self.phi * 4 * np.exp(-V/18)
        self.b_h = lambda V : self.phi / (np.exp((-V + 30)/10) + 1)
        self.I_L = lambda V : self.g_L * (V - self.V_L)
        self.I_K = lambda V, n :  self.g_K * n ** 4 * (V - self.V_K)
        self.I_Na = lambda V, m, h : self.g_Na * m ** 3 * h * (V - self.V_Na)

    def I(self, t):
        """Injected current as a function of time in nA/cm^2. """
        return 20 * (3 < t < 4)


    def diff_eq(self):
        """Returns function f such that the differential equations can be described as x' = f(t, x),
        where x = [V, n, m, h]."""
        def f(t, x):
            V, n, m, h = x
            y = np.zeros(4)
            y[0] = (self.I(t) - self.I_K(V, n) - self.I_Na(V, m, h) - self.I_L(V)) / self.C
            y[1] = self.a_n(V) * (1 - n) - self.b_n(V) * n
            y[2] = self.a_m(V) * (1 - m) - self.b_m(V) * m
            y[3] = self.a_h(V) * (1 - h) - self.b_h(V) * h
            return y
        return f

    def diff_eq_dynamic(self, K_guess):
        """Returns function f such that the differential equations can be described as x' = f(t, x),
        where x = [V, W, n, m, h]. W is a substitution variable for dV/dt. """
        def f(t, x):
            V, W, n, m, h = x
            y = np.zeros(5)
            y[0] = W
            y[1] = K_guess * (W + (self.I_K(V, n) + self.I_Na(V, m, h) + self.I_L(V)) / self.C)
            y[2] = self.a_n(V) * (1 - n) - self.b_n(V) * n
            y[3] = self.a_m(V) * (1 - m) - self.b_m(V) * m
            y[4] = self.a_h(V) * (1 - h) - self.b_h(V) * h
            return y
        return f

    def speed_from_K(self, K):
        """Return velocity in m/s from constant K. The factor 10 has to do with the units used for C and K."""
        return 10 * np.sqrt(K * self.a / (2 * self.R * self.C))

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
    
    def solve_dynamic_model(self, h, t, K_guess, quick=False):
        """Solves dynamic model using RK4 with step size h, for time (at least) t.
        If quick parameter is true then forward Euler is used.
        K_guess is a guess for the constant K from which the propagation speed can be determined."""
        N = np.int(np.ceil(t/h))
        f = self.diff_eq_dynamic(K_guess)
        y0 = np.array([self.V0, 0, self.n0, self.m0, self.h0])
        if quick:
            sol = tools.fe(f, 0, y0, h, N)
        else:
            sol = tools.rk4(f, 0, y0, h, N)
        return sol

if __name__ == "__main__":
    x = HodgkinHuxley()
    # t, y = x.solve_model(0.001, 30, True)
    # plt.plot(t, y[:,0], label="simple")
    K_guess = 10470
    print(x.speed_from_K(K_guess))
    #t, y = x.solve_dynamic_model(0.001, 20, K_guess, False)
    #plt.plot(t, y[:,0], label="dynamic")
    #plt.legend()
    #plt.show()