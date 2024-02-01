#!usr/bin/env python3
# coding=utf-8
"""
创建了一个鸡音盒，其中包含可点击的按钮，点击时会播放不同的声音。
"""
from pgzrun import *
from pgzero.actor import *
from pgzero.rect import *
from pgzero.keyboard import *

# 窗口大小：1010×576
WIDTH = 1010
HEIGHT = 576
# 标题：鸡音盒
TITLE = '鸡音盒'
# 创建角色
bg = Actor('bg.jpg')
leftSword = Actor('left.png', (60, 476))
rightSword = Actor('right.png', (950, 476))
b1 = Rect(100, 100, 100, 100)
b2 = Rect(225, 100, 100, 100)
b3 = Rect(350, 100, 100, 100)
b4 = Rect(475, 100, 100, 100)
b5 = Rect(600, 100, 140, 100)
b6 = Rect(770, 100, 140, 100)
b7 = Rect(100, 225, 225, 100)
b8 = Rect(350, 225, 225, 100)
b9 = Rect(600, 225, 310, 100)
b10 = Rect(100, 350, 390, 100)
b11 = Rect(520, 350, 390, 100)
# 默认在第一页
pg = 1
b1t = '鸡' if pg == 1 else '唱' if pg == 2 else '你'
b2t = '你' if pg == 1 else '跳' if pg == 2 else '干'
b3t = '太' if pg == 1 else 'rap' if pg == 2 else '嘛'
b4t = '美' if pg == 1 else '篮球' if pg == 2 else '哈哈'
b5t = '你干嘛~' if pg == 1 else 'music' if pg == 2 else '哎呦'
b6t = 'amagi' if pg == 1 else '喜欢' if pg == 2 else 'ma~'
b7t = '全民制作人' if pg == 1 else '全民制作人们' if pg == 2 else '啊~'
b8t = '练习时长两年半' if pg == 1 else '大家好' if pg == 2 else '哇真的是你呀'
b9t = '唱跳rap篮球' if pg == 1 else '我是' if pg == 2 else '哈哈哎呀'
b10t = '你干嘛哈哈哎呦' if pg == 1 else '练习两年半' if pg == 2 else '真的是你呀哈哈哎呀'
b11t = '呦哎哈哈嘛干你' if pg == 1 else '个人练习生' if pg == 2 else '呀哎哈哈呀你是的真'


def drawButton(rect: Rect, text: str):
    """
    该函数接受一个矩形和文本作为参数来绘制一个按钮

    :param rect: `rect` 参数是 `Rect` 类的一个实例，代表屏幕上的一个矩形区域。它包含有关矩形位置和大小的信息，
    例如其左上角坐标及其宽度和高度。此参数用于确定按钮的位置
    :type rect: Rect
    :param text: 将显示在按钮上的文本
    :type text: str
    """
    screen.draw.filled_rect(rect, '#1049E5')
    screen.draw.text(text, center=(rect.x+rect.width/2, rect.y+rect.height/2),
                     color=(255, 255, 255), fontsize=32, fontname='msyh')


def draw():
    """
    将背景和按钮绘制在窗口上
    """
    bg.draw()
    leftSword.draw()
    rightSword.draw()
    screen.draw.text('鸡音盒', center=(WIDTH/2, 50),
                     color=(16, 73, 229), fontsize=32, fontname='msyh')
    drawButton(b1, b1t)
    drawButton(b2, b2t)
    drawButton(b3, b3t)
    drawButton(b4, b4t)
    drawButton(b5, b5t)
    drawButton(b6, b6t)
    drawButton(b7, b7t)
    drawButton(b8, b8t)
    drawButton(b9, b9t)
    drawButton(b10, b10t)
    drawButton(b11, b11t)
    screen.draw.text(f'第{pg}页，共3页', center=(WIDTH/2, 513),
                     color=(16, 73, 229), fontsize=32, fontname='msyh')
    leftSword.show = pg == 2 or pg == 3
    rightSword.show = pg == 1 or pg == 2


def on_mouse_down(pos):
    """
    这是一个将鼠标点击的位置作为参数的函数。

    :param pos: “on_mouse_down”函数中的“pos”参数是指按下鼠标按钮时鼠标光标的位置。它通常是两个整数的元组，
    表示鼠标光标在屏幕上的 x 和 y 坐标。此参数可用于确定哪个对象
    """
    global pg, b1t, b2t, b3t, b4t, b5t, b6t, b7t, b8t, b9t, b10t, b11t
    if b1.collidepoint(pos):
        sounds.zhiyin.play() if pg == 1 else sounds.c.play() if pg == 2 else sounds.n.play()
    if b2.collidepoint(pos):
        sounds.ni.play() if pg == 1 else sounds.t.play() if pg == 2 else sounds.g.play()
    if b3.collidepoint(pos):
        sounds.tai.play() if pg == 1 else sounds.rap.play() if pg == 2 else sounds.m.play()
    if b4.collidepoint(pos):
        sounds.mei.play() if pg == 1 else sounds.lq.play() if pg == 2 else sounds.hh.play()
    if b5.collidepoint(pos):
        sounds.ngm.play() if pg == 1 else sounds.music.play() if pg == 2 else sounds.ay.play()
    if b6.collidepoint(pos):
        sounds.amagi.play() if pg == 1 else sounds.xh.play() if pg == 2 else sounds.ma.play()
    if b7.collidepoint(pos):
        sounds.qmzzr.play() if pg == 1 else sounds.qmzzrm.play() if pg == 2 else sounds.a.play()
    if b8.collidepoint(pos):
        sounds.lxsclnb.play() if pg == 1 else sounds.djh.play() if pg == 2 else screen.draw.text(
            '功能待开发', center=(WIDTH/2, HEIGHT/2), color=(0, 0, 0), fontsize=32, fontname='msyh')
    if b9.collidepoint(pos):
        sounds.ctrl.play() if pg == 1 else sounds.ws.play() if pg == 2 else screen.draw.text(
            '功能待开发', center=(WIDTH/2, HEIGHT/2), color=(0, 0, 0), fontsize=32, fontname='msyh')
    if b10.collidepoint(pos):
        sounds.ngmhhay.play() if pg == 1 else sounds.lxlnb.play() if pg == 2 else screen.draw.text(
            '功能待开发', center=(WIDTH/2, HEIGHT/2), color=(0, 0, 0), fontsize=32, fontname='msyh')
    if b11.collidepoint(pos):
        sounds.yahhmgn.play() if pg == 1 else sounds.grlxs.play() if pg == 2 else screen.draw.text(
            '功能待开发', center=(WIDTH/2, HEIGHT/2), color=(0, 0, 0), fontsize=32, fontname='msyh')
    if leftSword.collidepoint(pos):
        if pg != 1:
            pg -= 1
    if rightSword.collidepoint(pos):
        if pg != 3:
            pg += 1
    # 按钮内容重新定义
    b1t = '鸡' if pg == 1 else '唱' if pg == 2 else '你'
    b2t = '你' if pg == 1 else '跳' if pg == 2 else '干'
    b3t = '太' if pg == 1 else 'rap' if pg == 2 else '嘛'
    b4t = '美' if pg == 1 else '篮球' if pg == 2 else '哈哈'
    b5t = '你干嘛~' if pg == 1 else 'music' if pg == 2 else '哎呦'
    b6t = 'amagi' if pg == 1 else '喜欢' if pg == 2 else 'ma~'
    b7t = '全民制作人' if pg == 1 else '全民制作人们' if pg == 2 else '啊~'
    b8t = '练习时长两年半' if pg == 1 else '大家好' if pg == 2 else '哇真的是你呀'
    b9t = '唱跳rap篮球' if pg == 1 else '我是' if pg == 2 else '哈哈哎呀'
    b10t = '你干嘛哈哈哎呦' if pg == 1 else '练习两年半' if pg == 2 else '真的是你呀哈哈哎呀'
    b11t = '呦哎哈哈嘛干你' if pg == 1 else '个人练习生' if pg == 2 else '呀哎哈哈呀你是的真'


def on_key_down(key):
    """
    这是一个接受键参数并在按下键时执行某些操作的函数。
    
    :param key: 函数“on_key_down”中的“key”参数指的是用户按下的键盘按键。该参数通常是一个字符串或一个字符，表示按下的键。
    """
    global pg, b1t, b2t, b3t, b4t, b5t, b6t, b7t, b8t, b9t, b10t, b11t
    if key == keys.LEFT:
        if pg != 1:
            pg -= 1
    if key == keys.RIGHT:
        if pg != 3:
            pg += 1
    if key in (keys.LCTRL, keys.RCTRL) and pg == 1:
        sounds.ctrl.play()
    if key == keys.J and pg == 1:
        sounds.zhiyin.play()
    if key == keys.N and pg == 1:
        sounds.ni.play()
    if key == keys.T and pg == 1:
        sounds.tai.play()
    if key == keys.M and pg == 1:
        sounds.mei.play()
    if key == keys.A and pg == 1:
        sounds.amagi.play()
    if key == keys.Q and pg == 1:
        sounds.qmzzr.play()
    if key == keys.L and pg == 1:
        sounds.lxsclnb.play()
    if key == keys.C and pg == 2:
        sounds.c.play()
    if key == keys.T and pg == 2:
        sounds.t.play()
    if key == keys.R and pg == 2:
        sounds.rap.play()
    if key == keys.M and pg == 2:
        sounds.music.play()
    if key == keys.L and pg == 2:
        sounds.lq.play()
    if key == keys.X and pg == 2:
        sounds.xh.play()
    if key == keys.Q and pg == 2:
        sounds.qmzzrm.play()
    if key == keys.D and pg == 2:
        sounds.djh.play()
    if key == keys.W and pg == 2:
        sounds.ws.play()
    if key == keys.G and pg == 2:
        sounds.grlxs.play()
    if key == keys.N and pg == 3:
        sounds.n.play()
    if key == keys.G and pg == 3:
        sounds.g.play()
    if key == keys.M and pg == 3:
        sounds.m.play()
    if key == keys.H and pg == 3:
        sounds.hh.play()
    if key == keys.A and pg == 3:
        sounds.a.play()
    # 按钮内容重新定义
    b1t = '鸡' if pg == 1 else '唱' if pg == 2 else '你'
    b2t = '你' if pg == 1 else '跳' if pg == 2 else '干'
    b3t = '太' if pg == 1 else 'rap' if pg == 2 else '嘛'
    b4t = '美' if pg == 1 else '篮球' if pg == 2 else '哈哈'
    b5t = '你干嘛~' if pg == 1 else 'music' if pg == 2 else '哎呦'
    b6t = 'amagi' if pg == 1 else '喜欢' if pg == 2 else 'ma~'
    b7t = '全民制作人' if pg == 1 else '全民制作人们' if pg == 2 else '啊~'
    b8t = '练习时长两年半' if pg == 1 else '大家好' if pg == 2 else '哇真的是你呀'
    b9t = '唱跳rap篮球' if pg == 1 else '我是' if pg == 2 else '哈哈哎呀'
    b10t = '你干嘛哈哈哎呦' if pg == 1 else '练习两年半' if pg == 2 else '真的是你呀哈哈哎呀'
    b11t = '呦哎哈哈嘛干你' if pg == 1 else '个人练习生' if pg == 2 else '呀哎哈哈呀你是的真'


go()
