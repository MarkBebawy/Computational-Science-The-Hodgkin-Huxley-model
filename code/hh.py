def hh_v1(C, I, V0, n0, m0, h0, V_Na, V_K, V_L, g_K, g_Na, g_L, N, h)
    """
    Solves the Hodgkin-Huxley equations. 

    Parameters:
    C: Membrane capacitance
    I: Applied current (assumed constant)
    V0: Applied voltage at starting time
    m0: Initial probability of Na gate being open
    h0: Initial probability of Na gate being inactivated
    n0: Initial probability of K gate being open
    V_Na: Reverse potential of Na channel
    V_K: Reverse potential of K channel
    V_L: Reverse potential of leakage channel
    g_Na: Maximum Na conductance
    g_K: Maximum K conductance
    g_L: Maximum leakage conductance
    N: Number of steps to perform rk4
    h: Step size

    Returns:
    A 4 x (N+1) matrix containing computed solutions for I, n, m, h respectively.
    """
    
