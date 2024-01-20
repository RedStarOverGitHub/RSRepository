import turtle as t
from math import pi, sqrt
# 配置
size = 25
t.bgcolor('red')
t.pencolor('yellow')
t.pensize(size)
# 画镰刀
t.left(135)
t.forward(200)
t.left(90)
t.forward(50)
t.right(90)
t.forward(25)
t.right(90)
t.forward(75)
t.right(45)
t.forward(sqrt(25**2*2))
t.right(135)
t.forward(50)
# ----
t.penup()
t.forward(125)
# 画锤子
t.pendown()
t.forward(75)
t.backward(75)
t.left(90)
t.circle(150, 180)
for i in range(50):
    size -= 1/2
    t.pensize(size)
    t.circle(150, 1)
t.hideturtle()
t.done()
