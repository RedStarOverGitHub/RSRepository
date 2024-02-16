#!usr/bin/env python3
# coding=utf-8
"""
本代码的功能：
生成工具箱
"""
import tkinter as tk
import tkinter.scrolledtext as st
import tkinter.messagebox as msgbox
import tkinter.filedialog as filedia
import tkinter.ttk as ttk
from random import choice

import jieba as j


def marketAccountCopyGenrator():
    """
    生成营销号生成器功能窗口
    """
    marketAccountCopyGenrator = tk.Toplevel(main)  # 创建营销号生成器子窗口
    marketAccountCopyGenrator.geometry('600x250')  # 默认窗口大小：600×250
    marketAccountCopyGenrator.title('营销号生成器')  # 标题：“营销号生成器”
    templable = '''{0}{1}是怎么回事呢？{0}相信大家都很熟悉，但是{0}{1}是怎么回事呢，下面就让小编带大家一起了解吧。

    {0}{1}，其实就是{2}，大家可能会惊讶{0}怎么会{1}呢？但事实就是这样，小编也感到非常惊讶。

    这就是关于{0}{1}的事情了，大家有什么想法呢，欢迎在评论区告诉小编一起讨论哦！'''  # 营销号文案模板
    labelStyle = ttk.Style()
    labelStyle.configure('t.Label', background='#0080FF', foreground='#FFF')
    # 标题
    ttk.Label(marketAccountCopyGenrator, text='营销号生成器').place(relx=0, rely=0, relwidth=1, relheight=1/5)
    # 标题框
    ttk.Label(marketAccountCopyGenrator, text='输入', style='t.Label').place(relx=0, rely=2/10,
                                                                           relwidth=1/2, relheight=1/10)
    ttk.Label(marketAccountCopyGenrator, text='结果', style='t.Label').place(relx=1/2, rely=2/10,
                                                                           relwidth=1/2, relheight=1/10)
    ttk.Label(marketAccountCopyGenrator, text='名字：').place(relx=0, rely=3/10, relwidth=1/2, relheight=1/10)
    ttk.Label(marketAccountCopyGenrator, text='事件：').place(relx=0, rely=5/10, relwidth=1/2, relheight=1/10)
    ttk.Label(marketAccountCopyGenrator, text='另一种说法：').place(relx=0, rely=7/10, relwidth=1/2, relheight=1/10)
    # 输入框
    name = ttk.Entry(marketAccountCopyGenrator)
    name.place(relx=0, rely=4/10, relwidth=1/2, relheight=1/10)
    event = ttk.Entry(marketAccountCopyGenrator)
    event.place(relx=0, rely=6/10, relwidth=1/2, relheight=1/10)
    another = ttk.Entry(marketAccountCopyGenrator)
    another.place(relx=0, rely=8/10, relwidth=1/2, relheight=1/10)

    def generateCopy():
        """
        根据输入的三个内容按照模板生成文案
        """
        if not (name.get() and event.get() and another.get()):
            msgbox.showinfo('营销号生成器', '请将三个输入框全部输入')
        else:
            generateZone.delete(1.0, tk.END)
            generateZone.insert(tk.INSERT, templable.format(
                name.get(), event.get(), another.get()))

    # 生成区
    generateZone = st.ScrolledText(marketAccountCopyGenrator, bg='#FFF')
    generateZone.place(relx=1/2, rely=3/10, relwidth=1/2, relheight=7/10)
    # 按钮
    ttk.Button(marketAccountCopyGenrator, text='生成', command=generateCopy).place(
        relx=0, rely=9/10, relwidth=1/4, relheight=1/10)
    ttk.Button(marketAccountCopyGenrator, text='复制', command=lambda: generateZone.event_generate(
        '<<Copy>>')).place(relx=1/4, rely=9/10, relwidth=1/4, relheight=1/10)


def turntable():
    """
    生成转盘功能窗口
    """
    turntable = tk.Toplevel(main)  # 创建转盘子窗口
    turntable.geometry('400x200')  # 默认窗口大小：400×200
    turntable.title('转盘')  # 标题：“转盘”
    turntableResult, turntableInfomation = tk.StringVar(turntable), []  # 定义转盘结果显示变量和转盘列表

    def startTurntable():
        """
        开始抽奖，在抽奖列表中随机选一个元素
        """
        try:
            turntableResult.set(choice(turntableInfomation))
        except:
            turntableResult.set('')
            msgbox.showwarning('转盘', '请先设置转盘内容')

    def edit():
        """
        编辑转盘内容
        """
        edit = tk.Toplevel(turntable)  # 创建编辑子窗口
        edit.geometry('600x400')  # 默认窗口大小：600×400
        edit.title('编辑')  # 标题：“编辑”

        def preview():
            """
            预览转盘内容
            """
            global infomation
            infomation = tk.Listbox(edit, width=20, selectmode=tk.EXTENDED)  # 定义转盘内容预览区
            infomation.place(relx=2/3, rely=1/4, relwidth=1/3, relheight=3/4)
            infomation.insert(0, *turntableInfomation)
            horizontalScrollBar = ttk.Scrollbar(infomation, orient=tk.HORIZONTAL)
            horizontalScrollBar.pack(side=tk.BOTTOM, fill=tk.X)
            infomation.config(xscrollcommand=horizontalScrollBar.set)
            horizontalScrollBar.config(command=infomation.xview)

        def add():
            """
            添加转盘内容
            """
            turntableInfomation.insert(int(digits.get())-1, addInfomation.get())
            preview()

        def delete():
            """
            删除选中的转盘内容
            """
            for i in infomation.curselection():
                del turntableInfomation[i]
            preview()

        def openFile():
            """
            打开文件内容
            """
            try:
                path = filedia.askopenfilename(filetypes=[('txt', '*.txt'), ('All Files', '*.*')])
                if path:  # 判断路径是否为空
                    txt = open(path, encoding='utf-8')  # 打开文件
                    empty()  # 清空转盘内容
                    # 将文件内容添加到列表
                    for i in txt.readlines():
                        turntableInfomation.append(i[:-1])
                    txt.close()  # 关闭文件
                    preview()
            except:
                msgbox.showerror('编辑', '文件打开失败')

        def empty():
            """
            清空转盘内容
            """
            global turntableInfomation
            turntableInfomation = []
            preview()

        preview()
        ttk.Label(edit, text='转盘内容').place(relx=2/3, rely=0, relwidth=1/3, relheight=1/4)
        ttk.Label(edit, text='在第').place(relx=0, rely=0, relwidth=2/9, relheight=1/4)
        digits = ttk.Entry(edit)
        digits.place(relx=2/9, rely=0, relwidth=2/9, relheight=1/4)
        ttk.Label(edit, text='位').place(relx=4/9, rely=0, relwidth=1/9, relheight=1/4)
        addButton = ttk.Button(edit, text='添加', command=add)  # 定义添加按钮
        addButton.place(relx=5/9, rely=0, relwidth=1/9, relheight=1/4)
        addInfomation = ttk.Entry(edit)  # 定义添加的内容
        addInfomation.place(relx=0, rely=1/4, relwidth=2/3, relheight=1/4)
        deleteButton = ttk.Button(edit, text='删除选中内容', command=delete)
        deleteButton.place(relx=0, rely=2/4, relwidth=2/3, relheight=1/4)
        openFileButton = ttk.Button(edit, text='打开文件', command=openFile)
        openFileButton.place(relx=0, rely=3/4, relwidth=1/3, relheight=1/4)
        emptyButton = ttk.Button(edit, text='清空', command=empty)
        emptyButton.place(relx=1/3, rely=3/4, relwidth=1/3, relheight=1/4)

    ttk.Label(turntable, textvariable=turntableResult).place(relx=0, rely=0, relwidth=1, relheight=1/2)
    ttk.Button(turntable, text='开始', command=startTurntable).place(relx=0, rely=1/2, relwidth=1/2, relheight=1/2)
    ttk.Button(turntable, text='编辑', command=edit).place(relx=1/2, rely=1/2, relwidth=1/2, relheight=1/2)


def BMICaluclator():
    """
    生成BMI计算器功能窗口
    """
    BMICaluclator = tk.Toplevel(main)  # 创建BMI计算器子窗口
    BMICaluclator.geometry('400x200')  # 默认窗口大小：400×200
    BMICaluclator.title('BMI计算器')  # 标题：“BMI计算器”
    BMIResult = tk.StringVar(BMICaluclator)  # 定义BMI值显示变量
    BMIViewStyle = ttk.Style()
    BMIViewStyle.configure('t.Label')

    def calculateBMI():
        """
        计算BMI值，并显示范围
        """
        if weight.get() and height.get():
            try:
                BMI = round(eval(weight.get())/eval(height.get())**2, 2)
                if BMI < 18.5:
                    BMIViewStyle.configure('t.Label', background='#ff8000', foreground='#fff')
                    BMIResult.set(f'{BMI:.2f}\n身体状态：偏廋')
                elif 18.5 <= BMI < 24:
                    BMIViewStyle.configure('t.Label', background='#0f0', foreground='#000')
                    BMIResult.set(f'{BMI:.2f}\n身体状态：正常')
                elif 24 <= BMI < 28:
                    BMIViewStyle.configure('t.Label', background='#ff0', foreground='#000')
                    BMIResult.set(f'{BMI:.2f}\n身体状态：超重')
                elif BMI >= 28:
                    BMIViewStyle.configure('t.Label', background='#f00', foreground='#fff')
                    BMIResult.set(f'{BMI:.2f}\n身体状态：肥胖')
            except:
                msgbox.showerror('BMI计算器', '输入的内容必须是数字')
        else:
            msgbox.showinfo('BMI计算器', '请先输入身高和体重')

    ttk.Label(BMICaluclator, text='身高：\n（单位：米）').place(relx=0, rely=0, relwidth=1/4, relheight=1/2)
    height = ttk.Entry(BMICaluclator)
    height.place(relx=1/4, rely=0, relwidth=1/4, relheight=1/2)
    ttk.Label(BMICaluclator, text='体重：\n（单位：千克）').place(relx=0, rely=1/2, relwidth=1/4, relheight=1/2)
    weight = ttk.Entry(BMICaluclator)
    weight.place(relx=1/4, rely=1/2, relwidth=1/4, relheight=1/2)
    BMIView = ttk.Label(BMICaluclator, textvariable=BMIResult, style='t.Label')
    BMIView.place(relx=1/2, rely=0, relwidth=1/2, relheight=1/4)
    ttk.Button(BMICaluclator, text='计算BMI', command=calculateBMI).place(relx=1/2, rely=1/4, relwidth=1/2,
                                                                        relheight=1/4)
    # 设置对照表格
    columns = ('range', 'state')
    controlForm = ttk.Treeview(BMICaluclator, show='headings', columns=columns, selectmode=tk.BROWSE)
    # 指定列
    controlForm.column('range', anchor='w', width=12, stretch=True)
    controlForm.column('state', anchor='w', width=2, stretch=True)
    controlForm.heading('range', text='范围')
    controlForm.heading('state', text='状态')
    # 设置每行元素
    controlForm.insert('', 0, values=('BMI<18.5', '偏瘦'))
    controlForm.insert('', 1, values=('18.5≤BMI<24', '正常'))
    controlForm.insert('', 2, values=('24≤BMI<28', '超重'))
    controlForm.insert('', 3, values=('BMI≥28', '肥胖'))
    controlForm.place(relx=1/2, rely=1/2, relwidth=1/2, relheight=1/2)
    BMICaluclator.mainloop()


def tokenizer():
    """
    生成分词器窗口
    """
    tokenizer = tk.Toplevel(main)  # 创建分词器子窗口
    tokenizer.geometry('400x400')  # 默认窗口大小：200×400
    tokenizer.title('分词器')  # 标题：“分词器”
    mode = tk.StringVar(tokenizer)  # 定义模式变量
    mode.set('精确模式')  # 默认设置为精确模式
    isHMMMode = tk.BooleanVar()  # 定义是否开启HMM模式变量
    isHMMMode.set(True)  # 默认开启HMM模式

    def participle():
        """
        使输入框的内容分词
        """
        if mode.get() == '精确模式':
            resultZone.delete(1.0, tk.END)
            resultZone.insert(tk.INSERT, separator.get().join(j.lcut(inputZone.get(1.0, tk.END), HMM=isHMMMode.get())))
        elif mode.get() == '全模式':
            resultZone.delete(1.0, tk.END)
            resultZone.insert(tk.INSERT, separator.get().join(j.lcut(inputZone.get(1.0, tk.END), cut_all=True,
                                                                     HMM=isHMMMode.get())))
        elif mode.get() == '搜索引擎模式':
            resultZone.delete(1.0, tk.END)
            resultZone.insert(tk.INSERT, separator.get().join(j.lcut_for_search(inputZone.get(1.0, tk.END),
                                                                                HMM=isHMMMode.get())))

    def loadUserDict():
        """
        导入用户字典
        """
        try:
            path = filedia.askopenfilename(filetypes=[('txt', '*.txt'), ('All Files', '*.*')])
            if path:  # 判断路径是否为空
                j.load_userdict(path)  # 导入用户字典
        except:
            msgbox.showerror('分词器', '用户字典导入失败')

    ttk.Button(tokenizer, text='导入用户字典', command=loadUserDict).place(relx=0, rely=0, relwidth=1/2, relheight=1/8)
    ttk.Label(tokenizer, text='输入').place(relx=0, rely=1/8, relwidth=1/2, relheight=1/8)
    inputZone = st.ScrolledText(tokenizer, bg='#fff')
    inputZone.place(relx=0, rely=1/4, relwidth=1/2, relheight=1/2)
    precisionMode = ttk.Radiobutton(tokenizer, text='精确模式', variable=mode, value='精确模式')
    precisionMode.place(relx=0, rely=3/4, relwidth=1/4, relheight=1/8)
    fullMode = ttk.Radiobutton(tokenizer, text='全模式', variable=mode, value='全模式')
    fullMode.place(relx=1/4, rely=3/4, relwidth=1/4, relheight=1/8)
    scrachEngineMode = ttk.Radiobutton(tokenizer, text='搜索引擎模式', variable=mode, value='搜索引擎模式')
    scrachEngineMode.place(relx=0, rely=7/8, relwidth=1/4, relheight=1/8)
    hmmMode = ttk.Checkbutton(tokenizer, text='HMM模式', variable=isHMMMode, onvalue=True, offvalue=False)
    hmmMode.place(relx=1/4, rely=7/8, relwidth=1/4, relheight=1/8)
    ttk.Label(tokenizer, text='分隔符：').place(relx=1/2, rely=0, relwidth=1/4, relheight=1/8)
    separator = ttk.Entry(tokenizer)
    separator.insert(tk.INSERT, '/')
    separator.place(relx=3/4, rely=0, relwidth=1/4, relheight=1/8)
    ttk.Label(tokenizer, text='结果').place(relx=1/2, rely=1/8, relwidth=1/2, relheight=1/8)
    resultZone = st.ScrolledText(tokenizer, bg='#fff')
    resultZone.place(relx=1/2, rely=1/4, relwidth=1/2, relheight=1/2)
    ttk.Button(tokenizer, text='分词', command=participle).place(relx=1/2, rely=3/4, relwidth=1/2, relheight=1/4)
    tokenizer.mainloop()


def lenghtUnitCoverter():
    """
    生成长度单位转换窗口
    """
    lenghtUnitCoverter = tk.Toplevel(main)  # 创建长度单位转换器窗口
    lenghtUnitCoverter.geometry('400x300')  # 默认窗口大小：400×300
    lenghtUnitCoverter.title('长度单位转换器')  # 标题：“长度单位转换器”
    lengthUnits = ('千米 km', '米 m', '分米 dm', '厘米 cm', '毫米 mm', '微米 μm', '纳米 nm', '皮米 pm',
                   '海里 n mile', '英里 mi', '码 yd', '英尺 ft', '英寸 in',
                   '里', '丈', '尺', '寸', '分', '厘', '毫')  # 创建单位表

    def unitCovert(event):
        """
        长度单位转换
        """
        try:
            if unit1.get() in lengthUnits and unit2.get() in lengthUnits:
                covertForm = (0.001, 1, 10, 100, 1000, 1000000, 1000000000, 1000000000000, 1853.3, 0.0006214,
                              1.0936133, 3.2808399, 39.3700787, 0.002, 0.3, 3, 30, 300, 3000, 30000)  # 创建单位转换表
                unit1Index = lengthUnits.index(unit1.get())  # 映射索引
                unit2Index = lengthUnits.index(unit2.get())
                result.set(str(eval('%e' % (float(value.get())/covertForm[unit1Index]*covertForm[unit2Index]))))
        except:
            msgbox.showerror('长度单位转换器', '只能输入数字')

    result = tk.StringVar(lenghtUnitCoverter)  # 创建结果显示变量
    # 布局界面
    ttk.Label(lenghtUnitCoverter, text='长度单位转换器').place(relx=0, rely=0, relwidth=1, relheight=1/3)
    unit1 = ttk.Combobox(lenghtUnitCoverter, values=lengthUnits, state='readonly')
    unit1.bind('<<ComboboxSelected>>', unitCovert)
    unit1.place(relx=0, rely=1/3, relwidth=1/2, relheight=1/3)
    unit2 = ttk.Combobox(lenghtUnitCoverter, values=lengthUnits, state='readonly')
    unit2.bind('<<ComboboxSelected>>', unitCovert)
    unit2.place(relx=1/2, rely=1/3, relwidth=1/2, relheight=1/3)
    value = ttk.Entry(lenghtUnitCoverter)
    value.bind('<Return>', unitCovert)
    value.place(relx=0, rely=2/3, relwidth=1/2, relheight=1/3)
    ttk.Label(lenghtUnitCoverter, textvariable=result).place(relx=1/2, rely=2/3, relwidth=1/2, relheight=1/3)
    lenghtUnitCoverter.mainloop()


def areaUnitCoverter():
    """
    生成面积单位转换窗口
    """
    areaUnitCoverter = tk.Toplevel(main)  # 创建面积单位转换器窗口
    areaUnitCoverter.geometry('400x300')  # 默认窗口大小：400×300
    areaUnitCoverter.title('面积单位转换器')  # 标题：“面积单位转换器”
    areaUnits = ('平方千米 km²', '公顷 hm²', '公亩 are', '平方米 m²', '平方分米 dm²', '平方厘米 cm²', '平方毫米 mm²',
                 '英亩 acre', '平方英里 mi²', '平方码 yd²', '平方英尺 ft²', '平方英寸 in²',
                 '顷', '亩', '分', '平方尺', '平方寸')  # 创建单位表

    def unitCovert(event):
        """
        面积单位转换
        """
        try:
            if unit1.get() in areaUnits and unit2.get() in areaUnits:
                covertForm = (1e-6, 0.0001, 0.01, 1, 100, 10000, 1000000, 0.0002471, 3.8610e-7, 1.1959005, 10.7639104,
                              1550.0031, 0.000015, 0.0015, 0.015, 9, 900)  # 创建单位转换表
                unit1Index = areaUnits.index(unit1.get())  # 映射索引
                unit2Index = areaUnits.index(unit2.get())
                result.set(str(eval('%e' % (float(value.get())/covertForm[unit1Index]*covertForm[unit2Index]))))
        except:
            msgbox.showerror('面积单位转换器', '只能输入数字')

    result = tk.StringVar(areaUnitCoverter)
    # 布局界面
    ttk.Label(areaUnitCoverter, text='面积单位转换器').place(relx=0, rely=0, relwidth=1, relheight=1/3)
    unit1 = ttk.Combobox(areaUnitCoverter, values=areaUnits, state='readonly')
    unit1.bind('<<ComboboxSelected>>', unitCovert)
    unit1.place(relx=0, rely=1/3, relwidth=1/2, relheight=1/3)
    unit2 = ttk.Combobox(areaUnitCoverter, values=areaUnits, state='readonly')
    unit2.bind('<<ComboboxSelected>>', unitCovert)
    unit2.place(relx=1/2, rely=1/3, relwidth=1/2, relheight=1/3)
    value = ttk.Entry(areaUnitCoverter)
    value.bind('<Return>', unitCovert)
    value.place(relx=0, rely=2/3, relwidth=1/2, relheight=1/3)
    ttk.Label(areaUnitCoverter, textvariable=result).place(relx=1/2, rely=2/3, relwidth=1/2, relheight=1/3)
    areaUnitCoverter.mainloop()


def volumeUnitCoverter():
    """
    生成长度单位转换窗口
    """
    volumeUnitCoverter = tk.Toplevel(main)  # 创建体积单位转换器窗口
    volumeUnitCoverter.geometry('400x300')  # 默认窗口大小：400×300
    volumeUnitCoverter.title('体积单位转换器')  # 标题：“体积单位转换器”
    lengthUnits = ('立方千米 km³', '立方米 m³', '立方分米 dm³', '立方厘米 cm³', '立方毫米 mm³',
                   '公石 hL', '升 L', '分升 dL', '厘升 cL', '毫升 mL', '微升 μL',
                   '亩·英尺 acre.inch', '立方码 yd³', '立方英尺 ft³', '立方英寸 in³',
                   '英制加仑 Bgal', '美制加仑 Agal', '英制液体盎司 Boz', '美制液体盎司 Aoz')  # 创建单位表

    def unitCovert(event):
        """
        体积单位转换
        """
        try:
            if unit1.get() in lengthUnits and unit2.get() in lengthUnits:
                covertForm = (1e-9, 1, 1000, 1000000, 1000000000, 10, 1000, 10000, 100000, 1000000, 1000000000,
                              0.0008107, 1.3079528, 35.3147248, 61023.8445022, 219.9691573, 264.1720524, 35198.873636,
                              33818.0588434)  # 创建单位转换表
                unit1Index = lengthUnits.index(unit1.get())  # 映射索引
                unit2Index = lengthUnits.index(unit2.get())
                result.set(str(eval('%e' % (float(value.get())/covertForm[unit1Index]*covertForm[unit2Index]))))
        except:
            msgbox.showerror('体积单位转换器', '只能输入数字')

    result = tk.StringVar(volumeUnitCoverter)  # 创建结果显示变量
    # 布局界面
    ttk.Label(volumeUnitCoverter, text='体积单位转换器').place(relx=0, rely=0, relwidth=1, relheight=1/3)
    unit1 = ttk.Combobox(volumeUnitCoverter, values=lengthUnits, state='readonly')
    unit1.bind('<<ComboboxSelected>>', unitCovert)
    unit1.place(relx=0, rely=1/3, relwidth=1/2, relheight=1/3)
    unit2 = ttk.Combobox(volumeUnitCoverter, values=lengthUnits, state='readonly')
    unit2.bind('<<ComboboxSelected>>', unitCovert)
    unit2.place(relx=1/2, rely=1/3, relwidth=1/2, relheight=1/3)
    value = ttk.Entry(volumeUnitCoverter)
    value.bind('<Return>', unitCovert)
    value.place(relx=0, rely=2/3, relwidth=1/2, relheight=1/3)
    ttk.Label(volumeUnitCoverter, textvariable=result).place(relx=1/2, rely=2/3, relwidth=1/2, relheight=1/3)
    volumeUnitCoverter.mainloop()


def massUnitCoverter():
    """
    生成质量单位转换窗口
    """
    massUnitCoverter = tk.Toplevel(main)  # 创建体积单位转换器窗口
    massUnitCoverter.geometry('400x300')  # 默认窗口大小：400×300
    massUnitCoverter.title('质量单位转换器')  # 标题：“质量单位转换器”
    lengthUnits = ('吨 t', '公担 q', '千克 kg', '克 g', '毫克 mg', '微克 μg',
                   '长吨 lt', '短吨 sh.ton', '英担 Bcwt', '美担 Acwt', '英石 st', '磅 lb', '盎司 oz', '克拉 ct', '格令 gr',
                   '担', '斤', '两', '钱', '分')  # 创建单位表

    def unitCovert(event):
        """
        质量单位转换
        """
        try:
            if unit1.get() in lengthUnits and unit2.get() in lengthUnits:
                covertForm = (0.001, 0.01, 1, 1000, 1000000, 1000000000, 0.0009842, 0.0011023, 0.0196841, 0.0220462,
                              0.157473, 2.20466226, 35.2739619, 5000, 15432.3583529,
                              0.02, 2, 20, 200, 500000)  # 创建单位转换表
                unit1Index = lengthUnits.index(unit1.get())  # 映射索引
                unit2Index = lengthUnits.index(unit2.get())
                result.set(str(eval('%e' % (float(value.get())/covertForm[unit1Index]*covertForm[unit2Index]))))
        except:
            msgbox.showerror('质量单位转换器', '只能输入数字')

    result = tk.StringVar(massUnitCoverter)  # 创建结果显示变量
    # 布局界面
    ttk.Label(massUnitCoverter, text='质量单位转换器').place(relx=0, rely=0, relwidth=1, relheight=1/3)
    unit1 = ttk.Combobox(massUnitCoverter, values=lengthUnits, state='readonly')
    unit1.bind('<<ComboboxSelected>>', unitCovert)
    unit1.place(relx=0, rely=1/3, relwidth=1/2, relheight=1/3)
    unit2 = ttk.Combobox(massUnitCoverter, values=lengthUnits, state='readonly')
    unit2.bind('<<ComboboxSelected>>', unitCovert)
    unit2.place(relx=1/2, rely=1/3, relwidth=1/2, relheight=1/3)
    value = ttk.Entry(massUnitCoverter)
    value.bind('<Return>', unitCovert)
    value.place(relx=0, rely=2/3, relwidth=1/2, relheight=1/3)
    ttk.Label(massUnitCoverter, textvariable=result).place(relx=1/2, rely=2/3, relwidth=1/2, relheight=1/3)
    massUnitCoverter.mainloop()


def velocityUnitCoverter():
    """
    速度质量单位转换窗口
    """
    velocityUnitCoverter = tk.Toplevel(main)  # 创建体积单位转换器窗口
    velocityUnitCoverter.geometry('400x300')  # 默认窗口大小：400×300
    velocityUnitCoverter.title('速度单位转换器')  # 标题：“速度单位转换器”
    lengthUnits = ('光速 c', '马赫 mach', '节 kn', '千米/秒 km/s', '米/秒 m/s', '英尺/秒 ft/s', '英寸/秒 in/s',
                   '厘米/秒 cm/s', '英里/时 mi/h', '千米/时 km/h')  # 创建单位表

    def unitCovert(event):
        """
        速度单位转换
        """
        try:
            if unit1.get() in lengthUnits and unit2.get() in lengthUnits:
                covertForm = (3.3356e-9, 0.0029386, 1.944012, 0.001, 1, 3.28084,
                              39.370079, 100, 2.237136, 3600)  # 创建单位转换表
                unit1Index = lengthUnits.index(unit1.get())  # 映射索引
                unit2Index = lengthUnits.index(unit2.get())
                result.set(str(eval('%e' % (float(value.get())/covertForm[unit1Index]*covertForm[unit2Index]))))
        except:
            msgbox.showerror('速度单位转换器', '只能输入数字')

    result = tk.StringVar(velocityUnitCoverter)  # 创建结果显示变量
    # 布局界面
    ttk.Label(velocityUnitCoverter, text='速度单位转换器').place(relx=0, rely=0, relwidth=1, relheight=1/3)
    unit1 = ttk.Combobox(velocityUnitCoverter, values=lengthUnits, state='readonly')
    unit1.bind('<<ComboboxSelected>>', unitCovert)
    unit1.place(relx=0, rely=1/3, relwidth=1/2, relheight=1/3)
    unit2 = ttk.Combobox(velocityUnitCoverter, values=lengthUnits, state='readonly')
    unit2.bind('<<ComboboxSelected>>', unitCovert)
    unit2.place(relx=1/2, rely=1/3, relwidth=1/2, relheight=1/3)
    value = ttk.Entry(velocityUnitCoverter)
    value.bind('<Return>', unitCovert)
    value.place(relx=0, rely=2/3, relwidth=1/2, relheight=1/3)
    ttk.Label(velocityUnitCoverter, textvariable=result).place(relx=1/2, rely=2/3, relwidth=1/2, relheight=1/3)
    velocityUnitCoverter.mainloop()


def mainWindow():
    global main
    main = tk.Tk()  # 创建工具箱主窗口
    main.geometry('400x200')  # 默认窗口大小：400×200
    main.title('工具箱')  # 标题: “工具箱”

    ttk.Label(main, text='请选择工具').place(relx=0, rely=0, relwidth=1, relheight=1/4)
    ttk.Button(main, text='长度单位转换器', command=lenghtUnitCoverter).place(relx=0, rely=1/4, relwidth=1/3,
                                                                       relheight=1/4)
    ttk.Button(main, text='面积单位转换器', command=areaUnitCoverter).place(relx=1/3, rely=1/4, relwidth=1/3,
                                                                     relheight=1/4)
    ttk.Button(main, text='体积单位转换器', command=volumeUnitCoverter).place(relx=2/3, rely=1/4, relwidth=1/3,
                                                                       relheight=1/4)
    ttk.Button(main, text='营销号生成器', command=marketAccountCopyGenrator).place(relx=0, rely=1/2,
                                                                             relwidth=1/3, relheight=1/4)
    ttk.Button(main, text='转盘', command=turntable).place(relx=1/3, rely=1/2, relwidth=1/3, relheight=1/4)
    ttk.Button(main, text='质量单位转换器', command=massUnitCoverter).place(relx=2/3, rely=1/2, relwidth=1/3,
                                                                     relheight=1/4)
    ttk.Button(main, text='BMI计算器', command=BMICaluclator).place(relx=0, rely=3/4, relwidth=1/3, relheight=1/4)
    ttk.Button(main, text='分词器', command=tokenizer).place(relx=1/3, rely=3/4, relwidth=1/3, relheight=1/4)
    ttk.Button(main, text='速度单位转换器', command=velocityUnitCoverter).place(relx=2/3, rely=3/4, relwidth=1/3,
                                                                         relheight=1/4)
    main.mainloop()


mainWindow()
