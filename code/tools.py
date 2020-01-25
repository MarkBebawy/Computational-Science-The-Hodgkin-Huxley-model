import numpy as np

def rk4(f, t0, y0, h, N):
    """"Solve IVP given by y' = f(t, y), y(t_0) = y_0 with step size h > 0, for N steps."""
    t = t0 + np.array([i * h for i in range(N+1)])
    m = len(y0)
    y = np.zeros((N+1, m))
    y[0] = y0

    for n in range(N):
        k1 = f(t[n], y[n])
        k2 = f(t[n] + h/2, y[n] + k1 * h/2)
        k3 = f(t[n] + h/2, y[n] + k2 * h/2)
        k4 = f(t[n] + h, y[n] + k3 * h)
        y[n+1] = y[n] + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6

    return t, y

def fe(f, t0, y0, h, N):
    """"Solve IVP given by y' = f(t, y), y(t_0) = y_0 with step size h > 0, for N steps."""
    t = t0 + np.array([i * h for i in range(N+1)])
    m = len(y0)
    y = np.zeros((N+1, m))
    y[0] = y0

    for n in range(N):
        y[n+1] = y[n] + h*f(t[n], y[n])
    return t, y

def solve_quadratic(a, b, c):
    D = b ** 2 - 4 * a * c
    return (-b + np.sqrt(D)) / (2 * a), (-b - np.sqrt(D)) / (2 * a)

def bisect(f, x_low, x_high, n):
    """Apply bisection method n times to function f."""
    s = np.sign(f(x_low))
    t = np.sign(f(x_high))
    if s == t:
        # Betere manier nodig om error te gooien!
        return "Error: f(x_low) and f(x_high) have same sign"

    for _ in range(n):
        x = (x_low + x_high) / 2
        y = f(x)
        print(x)
        if y == 0:
            return x
        elif np.sign(y) == s:
            x_low = x
        else:
            x_high = x
    return (x_low + x_high) / 2
