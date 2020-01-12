import numpy as np

def rk4(f, t0, y0, h, N):
    """"Solve IVP given by y' = f(t, y), y(t_0) = y_0 with step size h > 0, for N steps."""
    t = t0 + np.array([i * h for i in range(N+1)]) 
    y = np.zeros(N+1)
    y[0] = y0
    
    for n in range(N):
        k1 = f(t[n], y[n])
        k2 = f(t[n] + h/2, y[n] + k1 * h/2)
        k3 = f(t[n] + h/2, y[n] + k2 * h/2)
        k4 = f(t[n] + h, y[n] + k3 * h)
        y[n+1] = y[n] + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        
    return y
