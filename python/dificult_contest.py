def solve(s):
    
    t = []
    other = []
    
    for ch in s:
        if ch == 'T':
            t.append(ch)
        else:
            other.append(ch)
    return t + other

n = int(input())
for i in range(n):
    s = input().strip()
    print(solve(s))