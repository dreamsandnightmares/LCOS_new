import matplotlib.pyplot as plt
import numpy as np

def calculate_y(x):
    return 0.0876 * x**3 - 0.2941 * x**2 + 0.5128 * x**1 + 1.4373

# Plot the function
x = np.linspace(0, 2, 1000)
y = calculate_y(x)
plt.plot(x, y,label = 'test1')
plt.legend()

# Add a horizontal line at y = 0
plt.axhline(y=0, color='black', linestyle='--')

# Add a vertical line at x = 1 and x = 2
plt.axvline(x=0, color='red', linestyle='--')
plt.axvline(x=2, color='red', linestyle='--')

# Show the plot


def equation(x):
    return 0.0876 * x**3 - 0.2941 * x**2 + 0.5128 * x**1 + 1.4373

def bisection(a, b, y, tol=1e-6):
    fa = equation(a) - y
    fb = equation(b) - y
    if fa * fb > 0:
        return None
    while abs(b - a) > tol:
        c = (a + b) / 2
        fc = equation(c) - y
        if fc == 0:
            return c
        elif fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc
    return (a + b) / 2

y = 1.0
a = 0.0
b = 2.0




