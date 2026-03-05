t = int(input("Enter Number of Test Case: "))

while t>=0:
    a = int(input())
    b = int(input())
    
    count = 0
    x = a  * b
    
    if(a == b):
        print("OP : 0")
    elif(a * b == a or a * b == b):
        print("OP : 1")
    else:
        if(a * b == x):
            print("OP : 2")
    t -= 1
    