class HodgkinHuxley:
    """
    Class which stores parameters of HH model.

    Attributes:
    C: Membrane capacitance (mF/cm^2)
    I: Applied current, assumed constant (nA)
    V0: Applied voltage at starting time (mV)
    m0: Initial probability of Na gate being open
    h0: Initial probability of Na gate being inactivated
    n0: Initial probability of K gate being open
    V_Na: Reverse potential of Na channel (mV)
    V_K: Reverse potential of K channel (mV)
    V_L: Reverse potential of leakage channel (mV)
    g_Na: Maximum Na conductance (mS/cm^2)
    g_K: Maximum K conductance (mS/cm^2)
    g_L: Maximum leakage conductance (mS/cm^2)
    phi: Factor for temperature correction
    """
    def __init(self, T)__:
        self.C = 0.1
        self.I = 15
        self.V0 = -65
        self.m0 = 0.05
        self.h0 = 0.6
        self.n0 = 0.317
        self.V_Na = 50
        self.V_K = -77
        self.V_L = -54.4
        self.g_Na = 120
        self.g_K = 36
        self.g_L = 0.3
        self.phi = 3 ** ((T - 6.3) / 10)


def hh_v1(C, I, V0, n0, m0, h0, V_Na, V_K, V_L, g_K, g_Na, g_L, N, h)

    
