import numpy as np
import matplotlib.pyplot as plt

x=np.array([1,3,4,6], dtype=float)
y=np.array([0.63,2.05,4.08,10.78], dtype=float)

n=2
m=len(x)

x_sum=[np.sum(x**k) for k in range(2*n+1)]
y_sum=[np.sum((x**k)*y) for k in range(n+1)]

A=np.zeros((n+1, n+1))
B=np.zeros(n+1)

for i in range(n+1):
    for j in range(n+1):
        A[i,j]=x_sum[i+j]
    B[i]=y_sum[i]
    
a=np.linalg.solve(A,B)
print(f"Polinominal coefficients a0, a1, a3 are: ",a)

y_pred=np.zeros_like(x)
for i in range(n+1):
    y_pred+=a[i]*(x**i)
    

plt.scatter(x,y, label="Data Point", color="red")
plt.plot(x,y_pred, label="Degree 2 fitted curve", color="blue")
plt.legend()
plt.show()