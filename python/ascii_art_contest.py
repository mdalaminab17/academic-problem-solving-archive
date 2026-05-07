score = list(map(int,input().split()))

score.sort()

if score[2] - score[0] >= 10:
    print("check again")
else:
    print(score[1])