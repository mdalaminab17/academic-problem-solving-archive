import numpy as np
import matplotlib.pyplot as plt

x_value = np.array([1,3,5], dtype=float)
y_value = np.array([2,10,26], dtype=float)

x =2 

y = LagrangeIterpolation(x_value,y_value,x)
print("Ïnterpolated value at x", x ,"is : ",y)

def LagrangeIterpolation(x_value, y_value,x):
    n = len(x_value)
    result = 0
    for i in range(n):
        term = y_value[i]
        for j in range(n):
            if j != i:
                term = term * (x - x_value[j])/(x_value[i] - x_value[j])
        result += term
    return result
x_points = np.linspace(1,5,200)
print(x_points[1])


y_points  = []

for x in x_points:
    y = LagrangeIterpolation(x_value,y_value,x)
    y_points.append(y)
plt.plot(x_points, y_points,color = "blue", label = "Lagrange Polynomial")
plt.scatter(x_points, y_points,color = "red", label = "Data Point")
plt.xlabel(x)
plt.ylabel(y)
plt.legend()
plt.grid(True)
plt.show()
