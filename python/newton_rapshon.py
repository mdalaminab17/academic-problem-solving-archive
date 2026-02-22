from math import fabs

def f(x):
    return x**3 - 2 * x - 5

def f_derive(x):
    return 3*(x**2) - 2

def Newton(x0, max_itr=500, eps=1e-5):
    if f_derive(x0) == 0:
        print("Newton Raphson method in not applicable")
        return None

    itr = 1
    xr_old = x0

    while True:
        if f_derive(xr_old) == 0:
            print("Newton Raphson method in not applicable")
            return None

        xr_new = xr_old - (f(xr_old) / f_derive(xr_old))
        ae = fabs(xr_new - xr_old)
        xr_old = xr_new
        itr += 1

        if ae <= eps or itr > max_itr:
            break

    return xr_old

x = float(input("Enter initial guess: "))

xr = Newton(x)

if xr is not None:
    print(f"The root is at: {xr:.6f}")
    print(f"Functional value at root: {f(xr):.6f}")