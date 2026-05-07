x , y = map(int, input().split())
s = input()

count4 = s.count('4')
count8 = s.count('8')

print(count4, count8)

if count4+count8 >= max(x,y):
    print("YES")
elif count4 == 2*count8:
    print("YES")
elif 2*count8 > x+y:
    print("YES")
else:
    print("NO")