def counting_sort(arr):
    maxVal = max(arr)
    count = [0] * (maxVal + 1)
    
    for num in arr:
        count[num] += 1
        
    result = []
    for i in range(len(count)):
        result.extend( [i] * count[i])
        
    return result

arr = list(map(int, input().split()))    
print(counting_sort(arr)) 