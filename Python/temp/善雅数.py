#!usr/bin/env python3
# coding=utf-8
SYnDict = {}
for i in range(3, 10):
    for j in range(4, 10):
        SYnDict[1000*i+100*(i-2)+10*(j-3)+j] = (10*(j-3)+j, 10*i+(i-2))


def F(n):
    s = SYnDict[n][0]
    t = SYnDict[n][1]
    if n in SYnDict:
        return (((s+t)/3), s, t)
    else: 
        return None
    

for k in SYnDict:
    if F(k)[0] != int(F(k)[0]):
        continue
    elif (10*F(k)[1]+F(k)[2]+1) % 13 == 0:
        print(k)
