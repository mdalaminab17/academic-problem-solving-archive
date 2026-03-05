t = int(input("Enter Number of Test Case: "))

while t>0:
    a = int(input())
    b = int(input())
    
    count = 0
    x = a  * b
    
    if(a == b):
        print("OP : 0")
    elif(a % b == 0 or a % b == 0):
        print("OP : 1")
    else:
        print("OP : 2")
    
    t -= 1
    