def isT(x):
    xDDList = [i for i in range(1, x+1) if x % i == 0 and len(str(i)) == 2]
    for i in range(len(xDDList)):
        for j in range(i+1, len(xDDList)):
            if xDDList[i] % 10+xDDList[j] % 10 == 7 and xDDList[i]//10+xDDList[j]//10 == 8:
                return (True, xDDList[i], xDDList[j])
    return (False, None, None)


TnDict = {}
for i in range(100, 10000):
    if isT(i)[0]:
        TnDict[i] = (isT(i)[1], isT(i)[2])


def P(A):
    return (TnDict[A][0]//10 - TnDict[A][0] % 10) + (TnDict[A][1] % 10 + TnDict[A][1]//10)


def Q(A):
    return (TnDict[A][0]//10 + TnDict[A][0] % 10) - (TnDict[A][1] % 10 - TnDict[A][1]//10)


def F(A):
    return P(A) / Q(A)


for i in TnDict:
    if F(i) % 5 == 0:
        print(i)
