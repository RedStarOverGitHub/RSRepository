#!usr/bin/env python3
# coding=utf-8
"""
本代码目前已实现的功能：
四则运算、幂运算、三角函数运算、集合运算、解方程
其它数学运算、微积分运算、随机数生成、位运算
"""
import tkinter as tk
import tkinter.ttk as ttk
from random import randint as randint_, uniform as uniform_
from math import prod as prod_, dist as dist_
from cmath import infj as infj_, nanj as nanj_
from itertools import product as carprod_
from functools import partial

import sympy as sp
from sympy import I, E, pi, oo, GoldenRatio, nan as nan_, EulerGamma, zoo as zoo_
from sympy import Naturals, Naturals0, Complexes, Reals, Integers, Rationals
from sympy import factorial2, beta, factorial, gamma, Abs as Abs_, ceiling, floor as floor_, zeta, Subs, Derivative
from sympy import Mod as Mod_, Range as range_, conjugate, Sum, Product
from sympy import Complement, Union, Intersection, SymmetricDifference, FiniteSet, ConditionSet
from sympy import Li as Li_, polylog, li as li_, polygamma, Integral, Limit
from sympy import Eq, Le, Ge, Lt, Gt, Ne
# 数学函数
ceil, floor, gcd, lcm, dist, Mod, Σ, Π, O, ζ = ceiling, floor_, sp.gcd, sp.lcm, dist_, Mod_, Sum, Product, sp.O, zeta
itersumm, iterprod, conju, Abs, Range, randint, randfloat = sum, prod_, conjugate, Abs_, range_, randint_, uniform_
# 数学运算符函数
eq, le, ge, lt, gt, ne = Eq, Le, Ge, Lt, Gt, Ne
# 数学常用变量符号
w, x, y, a, b, c, α, β, θ, s, t, z, m, n, xi = sp.symbols('w x y a b c α β θ s t z m n xi')
# 数学常量，并添加了τ（2π）
Φ, γ, π, e, τ, i, Ø, inf, infj, nan = GoldenRatio, EulerGamma, pi, E, pi * 2, I, set(), oo, infj_, nan_
zoo, Inf, NaN, nanj, EmpeySet = zoo_, inf, nan, nanj_, Ø
# 集合类函数和常量
N, N_0, C, R, Z, Q, finset = Naturals, Naturals0, Complexes, Reals, Integers, Rationals, FiniteSet
comple, union, intsec, symdif, conset = Complement, Union, Intersection, SymmetricDifference, ConditionSet
# 高数类函数
Si, Ci, Shi, Chi, li, ψ, ʃ, diff, lim, d = (sp.Si, sp.Ci, sp.Shi, sp.Chi, li_, polygamma, Integral, sp.diff, Limit,
                                            Derivative)
# 三角函数
sin, cos, tan, cot, sec, csc = sp.sin, sp.cos, sp.tan, sp.cot, sp.sec, sp.csc
# 反三角函数
asin, acos, atan, acot, asec, acsc = sp.asin, sp.acos, sp.atan, sp.acot, sp.asec, sp.acsc
# 双曲三角函数
sinh, cosh, tanh, coth, sech, csch = sp.sinh, sp.cosh, sp.tanh, sp.coth, sp.sech, sp.csch
# 反双曲三角函数
asinh, acosh, atanh, acoth, asech, acsch = sp.asinh, sp.acosh, sp.atanh, sp.acoth, sp.asech, sp.acsch
# 第三级运算函数和积函数
log, ln, log2, lg = (sp.log, sp.ln, lambda x, /: stdNumber(sp.log(x, 2)), lambda x, /: stdNumber(sp.log(x, 10)))
exp, sqrt, Γ, Β, carprod = (sp.exp, sp.sqrt, gamma, beta, lambda *sets: set(carprod_(*sets)))
# 其他数学函数
root, cbrt, neg, summ = (sp.root, sp.cbrt, lambda x, /: stdNumber(-x), lambda *nums: stdNumber(itersumm(nums)))
rad, deg, prod, fact = (sp.rad, sp.deg, lambda *nums: stdNumber(iterprod(nums)),
                        lambda x, y=0, /: stdNumber(factorial2(x) if y else factorial(x)))
itermean, mean, fract, Li = (lambda iterable, /: stdNumber(sum(iterable)/len(iterable)),
                             lambda *nums: stdNumber(itermean(nums)),
                             lambda x=0, y=1, /: sp.Rational(str(x)) if y == 1 else sp.Rational(x, y),
                             lambda x, y=None: Li_(x) if y is None else polylog(y, x))

main = tk.Tk()  # 主窗口
main.title('科学计算器')  # 标题：“科学计算器”
main.geometry('750x400')  # 默认窗口大小：750×400
main.minsize(630, 360)  # 最小窗口大小：630×360
result = tk.StringVar()  # 结果显示变量
button = partial(ttk.Button, main)  # 统一函数
replaceDict = {'×': '*', '÷': '/', '%': '/100', '^': '**', ' mod ': '%', '∈': ' in ', '∉': ' not in ', '≠': '!=',
               '=': '==', '≥': '>=', '≤': '<=', '₀': '_0', '∨': '|', '∧': '&', '¬': '~', '⊻': '^'}  # 定义替换词典
calculateStack = []  # 定义计算栈
Ans = 0  # Ans变量初始为0


def stdNumber(value, /):
    """
    函数“stdNumber”接受一个位置参数“value”并且没有实现代码。

    :param value: 参数“value”是函数“stdNumber”的必需位置参数。它用正斜杠 (/) 表示，这意味着它只能作为位置参数而不是关键字参数传递。
    """
    try:
        # 过滤分数和复数
        if xor(complex(eval(str(value))) == complex(eval(str(value))).real,
               type(value) in (sp.Rational, type(fract(1, 2)))):
            try:
                # 过滤整数
                if xor(not round(float(eval(str(value)).real), 14).is_integer(),
                       -1e-14 < eval(str(value)).real < 1e-14):
                    if -1e-14 < eval(str(value)).real < 1e-14:
                        if float(eval(str(value)).real).is_integer():  # 二次过滤整数
                            return int(eval(str(value)).real)
                        return eval(str(value)).real
                    return round(eval(str(value)).real, 14)  # 防止因精度损失返回失真的结果
                return int(round(eval(str(value)).real, 14))
            except (OverflowError, ValueError):  # 处理±∞和nan
                if eval(str(value)).real >= 1.79e+308:
                    return inf
                elif eval(str(value)).real <= -1.79e+308:
                    return -inf
                return nan
        return complex(eval(str(value))) if type(value) not in (sp.Rational, type(fract(1, 2))) else value
    except (TypeError, AttributeError):
        try:
            # 过滤复数
            if complex(eval(str(value))) == complex(eval(str(value))).real:
                return complex(eval(str(value))).real
            return complex(eval(str(value)))
        except (TypeError, AttributeError):
            return eval(str(value))


def screenUpdate():
    """
    刷新算式显示区
    """
    result.set(''.join(calculateStack))


def xor(x, y, /):
    """
    名为“xor”的函数接受两个参数 x 和 y，并对它们执行异或运算。

    :param x: XOR 运算的第一个输入值。
    :param y: 参数“y”是函数“xor”的必需参数。调用函数时将其作为第二个参数传递。参数列表中的正斜杠表示后面的所有参数
    """
    return False if bool(x) == bool(y) else True


def replace(string: str, replaceDict: dict, /):
    """
    此函数采用一个字符串和一个替换值字典，并将字符串中所有出现的键替换为其对应的值。

    :param string: 我们要修改的字符串，方法是用 replaceDict 字典中相应的值替换某些子字符串。
    :type string: str
    :param replaceDict: replaceDict 参数是一个包含键值对的字典，其中键是要替换的子字符串，值是要替换它的子字符串。
    :type replaceDict: dict
    """
    for i in replaceDict:  # 根据字典长度替换
        string = string.replace(i, replaceDict[i])
    return string


def isiter(obj):
    """
    函数“isiter”检查一个对象是否可迭代。

    :param obj: 需要检查的对象是否可迭代。可迭代对象是可以循环的对象，例如列表、元组、字符串或字典。
    """
    return {'__iter__', '__getitem__'} < set(dir(eval(obj)))


def solve():
    """
    对输入框的表达式进行解方程
    """
    try:
        formula = eval(replace(view.get(), replaceDict))
        result_ = sp.solve(formula)
        if type(result_) != dict:
            for i in result_:
                if type(i) == dict:
                    calculateStack.append(i)
                    break
            else:
                calculateStack.append(set(result_))
        else:
            calculateStack.append(result_)
        calculate()
    except SyntaxError:
        ...


def expand():
    """
    对输入框的表达式进行展开
    """
    infomation = replace(view.get(), replaceDict)
    if infomation:
        calculateStack.append(f'sp.expand({infomation})')
    calculate()


def simplify():
    """
    对输入框的表达式进行简化
    """
    infomation = replace(view.get(), replaceDict)
    if infomation:
        calculateStack.append(f'sp.simplify({infomation})')
    calculate()


def series():
    """
    对输入框的表达式进行级数展开
    """
    infomation = replace(view.get(), replaceDict)
    if infomation:
        calculateStack.append(f'sp.series({infomation})')
    calculate()


def cv():
    """
    清空栈
    """
    calculateStack.clear()
    screenUpdate()


def bs():
    """
    删除输入框最后一个栈元素
    """
    del calculateStack[-1]
    screenUpdate()


def calculate():
    """
    计算输入框的内容
    """
    try:
        stdNum = stdNumber(eval(replace(view.get(), replaceDict)))
        # 过滤可迭代对象（集合除外）
        if not isiter(replace(view.get(), replaceDict)) and type(eval(replace(view.get(), replaceDict))) not in (bool,
                                                                                                                 set):
            # 使用科学计数法
            if len(str(stdNum).split('.')[0]) > 17 and type(stdNum) in (int, float, complex):
                calculateStack.append(str(eval('%e' % stdNum)))
            else:
                calculateStack.append(str(stdNum))
        else:
            if str(eval(replace(view.get(), replaceDict))) in ('set()', 'EmptySet'):  # 将所有表示空集的文字替换为Ø
                calculateStack.append(str(replace(str(eval(replace(view.get(), replaceDict))),
                                                  {'set()': 'Ø', 'EmptySet': 'Ø'})))
            elif type(eval(replace(view.get(), replaceDict))) == bool:  # 将布尔值正确表示为True/False
                calculateStack.append(str(eval(replace(view.get(), replaceDict))))
            else:
                calculateStack.append(str(eval(replace(view.get(), replaceDict))))  # 将集合正确显示在输入框上
    except OverflowError:
        calculateStack.append(str(inf))  # 若抛出溢出错误，显示inf
    except SyntaxError:
        ...  # 若显示区为空则忽略
    except ZeroDivisionError:
        calculateStack.append(str(zoo))  # 若抛出除零错误，显示nan+nani
    except:
        calculateStack.append('错误')
    del calculateStack[:-1]
    screenUpdate()


def secFn():
    """
    启动和关闭对应按钮的第二个功能
    """
    # 定义一个第二功能按钮布局
    secFnButtons = (
        (None, None, None, None, None, ('⌊x⌋', 'floor('), ('x!', 'fact'), ('³√x̅', 'cbrt'), ('iter\nsumm', 'itersumm'),
         ('rand\nint', 'randint'), ('∪', 'union'), ("'", 'diff'), ('sin⁻¹', 'asin'),
         ('sinh⁻¹', 'asinh'), ('O', 'O')),
        (None, None, None, None, ('lg', 'lg'), ('ln', 'ln'), ('ʸ√x̅', 'root'), ('x³', '^3'),
         ('iter\nprod', 'iterprod'), None, ('∩', 'intsec'), ('d', 'd'), ('cos⁻¹', 'acos'), ('cosh⁻¹', 'acosh'),
         ('ζ', 'ζ')),
        (None, None, None, None, ('τ', 'τ'), ('eˣ', 'exp('), ('i', 'i'), ('10ˣ', '10^'), ('iter\nmean', 'itermean'),
         None, ('\\', 'comple'), ('Li', 'Li'), ('tan⁻¹', 'atan'), ('tanh⁻¹', 'atanh'), ('Subs', 'Subs')),
        (None, None, None, None, ('lcm', 'lcm'), ('{', '{'), ('}', '}'), ('deg', 'deg'), ('X̅', 'mean'),
         ('prod', 'prod'), ('∆', 'symdif'), ('Shi', 'Shi'), ('cot⁻¹', 'acot'), ('coth⁻¹', 'acoth'), None),
        (None, None, None, None, None, None, ('Φ', 'Φ'), ('a', 'a'), ('b', 'b'), None, ('conset', 'conset'),
         ('Chi', 'Chi'), ('sec⁻¹', 'asec'), ('sech⁻¹', 'asech'), None),
        (('1\nx̅', '1÷'), None, (',', ','), None, None, None, ('w', 'w'), ('c', 'c'), ('m', 'm'), ('Γ', 'Γ'),
         ('finset', 'finset'), None, ('sec⁻¹', 'asec'), ('csch⁻¹', 'acsch'), None),
        (('¬', '¬'), ('⊻\n∆', '⊻'), ('>>', '>>'), ('≠', '≠'), ('≥\n⊇', '≥'), ('≤\n⊆', '≤'), ('dist', 'dist'),
         ('∉', '∉'), ('Range', 'Range'), ('Π', 'Π'), None, None, None, None, None)
    )
    secButtonList = []  # 定义第二功能按钮列表
    # 遍历并添加按钮
    for r in range(len(secFnButtons)):
        secButtonList.append([])  # 每一次大循环开始，按钮列表会添加一个空列表
        for c_ in range(len(secFnButtons[r])):
            # 判断是要添加None还是添加按钮
            if secFnButtons[r][c_] is None:
                secButtonList[r].append(None)
            else:
                secButtonList[r].append(button(text=secFnButtons[r][c_][0],
                                               command=lambda t=secFnButtons[r][c_][1]: addChar(t)))  # 添加按钮
    for r in range(len(secButtonList)):
        for c_ in range(len(secButtonList[r])):
            # 若元素的内容是None，跳过本次循环
            if secButtonList[r][c_] is None:
                continue
            else:
                secButtonList[r][c_].place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)  # 放置按钮

    def secFnOn():
        """
        关闭对应按钮的第二功能
        """
        # 遍历并销毁按钮
        for r in secButtonList:
            for c_ in r:
                if c_ is None:
                    continue
                else:
                    c_.destroy()
        # 2nd按钮
        secOnButton.destroy()

    secOnButton = button(text='2nd', command=secFnOn)
    secOnButton.place(relx=4/15, rely=1/8, relwidth=1/15, relheight=1/8)


def addChar(text):
    """
    它将一个文字转换成正确的内容并添加到输入框光标的前面

    :param text: 要添加到输入框的文本。
    """
    # 使用match-case语句，转换成正确的内容
    match text:
        case '2ˣ':
            calculateStack.append('2^')
        case 'x²':
            calculateStack.append('^2')
        case '√x̅':
            calculateStack.append('sqrt')
        case '⌈x⌉':
            calculateStack.append('ceil')
        case '|x|':
            calculateStack.append('Abs')
        case 'xʸ':
            calculateStack.append('^')
        case '+/-':
            calculateStack.append('neg')
        case 'rand\nfloat':
            calculateStack.append('randfloat')
        case '∨\n∪':
            calculateStack.append('∨')
        case '∧\n∩':
            calculateStack.append('∧')
        case '>\n⊋':
            calculateStack.append('>')
        case '<\n⊊':
            calculateStack.append('<')
        case 'car\nprod':
            calculateStack.append('carprod')
        case '∞':
            calculateStack.append('inf')
        case 'x\ny̅':
            calculateStack.append('fract')
        case 'z̅':
            calculateStack.append('conju')
        case 'iter\nsumm':
            calculateStack.append('itersumm')
        case 'iter\nprod':
            calculateStack.append('iterprod')
        case 'iter\nmean':
            calculateStack.append('itermean')
        case _:
            calculateStack.append(text)
    screenUpdate()


def sto():
    """
    Ans变量通过本函数赋值给输入框上内容的结果
    """
    global Ans
    try:
        stdNum = stdNumber(eval(replace(view.get(), replaceDict)))
        # 过滤非可迭代对象（集合除外）
        if not isiter(replace(view.get(), replaceDict)) and type(eval(replace(view.get(), replaceDict))) not in (bool,
                                                                                                                 set):
            Ans = stdNum
        else:
            if str(eval(replace(view.get(), replaceDict))) in ('set()', 'EmptySet'):  # Ans赋值为空集
                Ans = Ø
            elif type(eval(replace(view.get(), replaceDict))) == bool:
                Ans = bool(eval(replace(view.get(), replaceDict)))
            else:
                Ans = eval(replace(view.get(), replaceDict))  # Ans赋值为集合
    except OverflowError:
        Ans = inf  # 若抛出溢出错误，将Ans变量赋值为inf
    except SyntaxError:
        ...  # 若抛出语法错误，则忽略
    except ZeroDivisionError:
        Ans = zoo  # 若抛出除零错误，将Ans变量赋值为nan+nani


def mc():
    """
    Ans变量恢复初始值
    """
    global Ans
    Ans = 0


def ac():  # 全清
    """
    将输入框清空并将Ans变量恢复初始值
    """
    cv()
    mc()


ttk.Label(main, text='科学计算器', ).place(relx=0, rely=0, relwidth=1, relheight=1/16)  # 标题
view = ttk.Entry(main, justify=tk.RIGHT, textvariable=result)  # 显示算式或结果
# 键盘事件
view.bind('<Return>', lambda event: calculate())
view.bind('<Escape>', lambda event: ac())
view.bind('<Delete>', lambda event: cv())
view.bind('<Control-KeyPress-q>', lambda event: main.destroy())
view.bind('<Control-KeyPress-Q>', lambda event: main.destroy())
view.bind('<Control-KeyPress-m>', lambda event: sto())
view.bind('<Control-KeyPress-l>', lambda event: mc())
view.bind('<Control-KeyPress-r>', lambda event: calculateStack.append(tk.INSERT, 'Ans'))
view.bind('<Control-KeyPress-M>', lambda event: sto())
view.bind('<Control-KeyPress-L>', lambda event: mc())
view.bind('<Control-KeyPress-R>', lambda event: calculateStack.append(tk.INSERT, 'Ans'))

view.place(relx=0, rely=1/16, relwidth=1, relheight=1/16)

menu = tk.Menu(main)  # 创建菜单
option = tk.Menu(menu, tearoff=0)  # 创建子菜单，在顶部
menu.add_cascade(label='选项', menu=option)
# 子菜单选项
option.add_command(label='剪切', command=lambda: view.event_generate('<<Cut>>'), accelerator='Ctrl+X')
option.add_command(label='复制', command=lambda: view.event_generate('<<Copy>>'), accelerator='Ctrl+C')
option.add_command(label='粘贴', command=lambda: view.event_generate('<<Paste>>'), accelerator='Ctrl+V')
option.add_separator()  # 添加分割线
option.add_command(label='退出', command=main.destroy, accelerator='Ctrl+Q')
main.config(menu=menu)  # 将菜单添加到窗口
# 定义一个窗口的按钮布局元组
buttons = (('AC', 'MC', 'Ans', 'MS', '2nd', '⌈x⌉', '|x|', '√x̅', 'min', 'rand\nfloat', 'N', 'ʃ', 'sin', 'sinh', 'eq'),
           ('CV', '⌫', '%', '÷', 'log2', 'log', 'xʸ', 'x²', 'max', 'True', 'N₀', 'lim', 'cos', 'cosh', 'le'),
           ('7', '8', '9', '×', 'π', 'e', ' mod ', '2ˣ', 'len', 'False', 'Z', 'li', 'tan', 'tanh', 'ge'),
           ('4', '5', '6', '-', 'gcd', '(', ')', 'rad', 'car\nprod', 'summ', 'Q', 'Si', 'cot', 'coth', 'lt'),
           ('1', '2', '3', '+', 'α', 'β', 'γ', 'x', 'y', '∞', 'R', 'Ci', 'sec', 'sech', 'gt'),
           ('+/-', '0', '.', '计算', 'θ', 's', 't', 'z', 'n', 'Β', 'C', 'x\ny̅', 'csc', 'csch', 'ne'),
           ('∨\n∪', '∧\n∩', '<<', '=', '>\n⊋', '<\n⊊', 'round', '∈', 'Ø', 'Σ', '解方程', 'z̅', '简化\n表达式',
            '展开\n表达式', '级数\n展开'))

# 根据按钮布局生成按钮
for r in range(len(buttons)):
    for c_ in range(len(buttons[r])):
        if buttons[r][c_] == 'AC':
            button(text=buttons[r][c_], command=ac).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
        elif buttons[r][c_] == 'MC':
            button(text=buttons[r][c_], command=mc).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
        elif buttons[r][c_] == 'MS':
            button(text=buttons[r][c_], command=sto).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
        elif buttons[r][c_] == '计算':
            button(text=buttons[r][c_], command=calculate).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15,
                                                                 relheight=1/8)
        elif buttons[r][c_] == 'CV':
            button(text=buttons[r][c_], command=cv).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
        elif buttons[r][c_] == '⌫':
            button(text=buttons[r][c_], command=bs).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
        elif buttons[r][c_] == '2nd':
            button(text=buttons[r][c_], command=secFn).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
        elif buttons[r][c_] == '解方程':
            button(text=buttons[r][c_], command=solve).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
        elif buttons[r][c_] == '展开\n表达式':
            button(text=buttons[r][c_], command=expand).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
        elif buttons[r][c_] == '简化\n表达式':
            button(text=buttons[r][c_], command=simplify).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
        elif buttons[r][c_] == '级数\n展开':
            button(text=buttons[r][c_], command=series).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
        elif buttons[r][c_] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
            button(text=buttons[r][c_], command=lambda t=buttons[r][c_]: addChar(t)).place(
                relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
        else:
            button(text=buttons[r][c_], command=lambda t=buttons[r][c_]: addChar(
                t)).place(relx=c_/15, rely=(r+1)/8, relwidth=1/15, relheight=1/8)
main.mainloop()
