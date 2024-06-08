#!usr/bin/env python3
# coding=utf-8
"""
此为《Python少儿趣味编程》中“成绩单”项目的GUI版本
"""
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedia
import tkinter.messagebox as msgbox
import tkinter.simpledialog as sdialog

students = {}  # 学生信息存储字典


class Main:
    state = "new"  # 当前状态
    filePath = ""  # 当前导入文件的路径

    def __init__(self):  # 创建主界面
        self.main = tk.Tk()
        self.main.title("学生信息管理系统")
        self.main.geometry("600x300")
        self.main.protocol("WM_DELETE_WINDOW", self.__closeWindow)  # 关闭窗口
        mainMenu = tk.Menu(self.main)
        self.main.config(menu=mainMenu)
        menu1 = tk.Menu(mainMenu, tearoff=0)
        mainMenu.add_cascade(label="文件", menu=menu1)
        menu1.add_command(label="打开", command=self.__open)
        menu1.add_command(label="保存", command=self.__save)
        menu1.add_command(label="另存为", command=self.__saveAs)
        menu1.add_separator()
        menu1.add_command(label="退出", command=self.__closeWindow)
        menu2 = tk.Menu(mainMenu, tearoff=0)
        mainMenu.add_cascade(label="帮助", menu=menu2)
        menu2.add_command(label="关于", command=self.__about)

        # 创建标题
        ttk.Label(self.main, text="学生成绩管理系统").place(relx=0, rely=0, relwidth=1, relheight=1/3)
        # 创建按钮
        self.__generateButton("添加学生信息", self.__addStudent, 1, 1)
        self.__generateButton("删除学生信息", self.__deleteStudent, 2, 1)
        self.__generateButton("修改学生信息", self.__modifyStudent, 3, 1)
        self.__generateButton("查询学生信息", self.__queryStudent, 1, 2)
        self.__generateButton("查看学生信息", self.__viewStudent, 2, 2)
        self.__generateButton("查询学生总分", self.__queryStudentTscore, 3, 2)

        self.main.mainloop()

    def __open(self):  # 导入信息
        path = filedia.askopenfilename(filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        fail = False  # 判断信息是否导入失败
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f.readlines():
                        message = line[:-1].split()  # 使用空格分隔每行的信息
                        try:
                            if len(message) != 6:
                                msgbox.showerror("错误", "导入文件失败")
                                students.clear()
                                fail = True
                                break
                            students[int(message[0])] = [message[1], message[2], float(message[3]),
                                                         float(message[4]), float(message[5])]
                        except:
                            msgbox.showerror("错误", "导入文件失败")
                            students.clear()
                            fail = True
                            break
                if not fail:
                    self.state = "loaded"
                    self.filePath = path
            except:
                msgbox.showerror("错误", "导入文件失败")

    def __save(self):  # 保存信息
        if self.filePath:
            path = self.filePath
        else:
            path = filedia.asksaveasfilename(filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    for i in students:
                        f.write(f"{str(i)} {students[i][0]} {students[i][1]} {str(students[i][2])} "
                                f"{str(students[i][3])} {str(students[i][4])}\n")
                self.state = "loaded"
            except:
                msgbox.showerror("错误", "保存失败")

    def __saveAs(self):  # 另存为
        path = filedia.asksaveasfilename(filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    for i in students:
                        f.write(f"{str(i)} {students[i][0]} {students[i][1]} {str(students[i][2])} "
                                f"{str(students[i][3])} {str(students[i][4])}\n")
                self.state = "loaded"
            except:
                msgbox.showerror("错误", "保存失败")

    def __about(self):  # 关于
        msgbox.showinfo("关于", "学生成绩管理系统\n《Python少儿趣味编程》“成绩单”项目GUI版\n版本号：1.0\n作者：张三")

    def __queryStudentTscore(self):  # 查询学生总分
        query = tk.Toplevel(self.main)
        query.title("查询学生总分")
        query.geometry("600x100")
        ttk.Label(query, text="学号").place(relx=0, rely=0, relwidth=1/3, relheight=1)
        stuID = ttk.Entry(query)
        stuID.place(relx=1/3, rely=0, relwidth=1/3, relheight=1)

        def queryStudentTscore():
            try:
                name = students[int(stuID.get())][0]
                chinese = students[int(stuID.get())][2]
                math = students[int(stuID.get())][3]
                english = students[int(stuID.get())][4]
                msgbox.showinfo("查询结果", f"{name}的总分为{chinese+math+english}")
            except KeyError:
                msgbox.showerror("错误", "学号不存在")
            except ValueError:
                msgbox.showerror("错误", "学号非数字")

        ttk.Button(query, text="查询", command=queryStudentTscore).place(relx=2/3, rely=0, relwidth=1/3, relheight=1)
        query.mainloop()

    def __viewStudent(self):  # 浏览所有学生的信息
        viewStudent = tk.Toplevel(self.main)
        viewStudent.title("学生信息浏览")
        viewStudent.geometry("600x300")
        # 创建排序类型变量
        sortType = tk.IntVar(viewStudent)
        sortType.set(0)
        isSort = tk.BooleanVar(viewStudent)
        isSort.set(True)

        def updateRank():
            studentForm.delete(*studentForm.get_children())  # 覆盖原有的排名信息
            cnt = 0
            # 根据某个选项排序
            if sortType.get() == 0:
                sortedStudents = dict(sorted(students.items(), key=lambda x: x[0], reverse=not isSort.get()))
            elif sortType.get() == 4:
                sortedStudents = dict(sorted(students.items(), key=lambda x: sum(x[1][2:]), reverse=isSort.get()))
            else:
                sortedStudents = dict(sorted(students.items(), key=lambda x: x[1][sortType.get()+1],
                                             reverse=isSort.get()))
            # 遍历将学生信息添加到列表
            for i in sortedStudents:
                studentForm.insert("", cnt, values=(cnt+1, i, *sortedStudents[i], sum(sortedStudents[i][2:])))
                cnt += 1
            studentForm.place(relx=0, rely=0, relwidth=1, relheight=1)

        # 创建排序选项按钮
        sortOption = ttk.LabelFrame(viewStudent, text="排序选项")
        sortOption.place(relx=0, rely=0, relwidth=1, relheight=1/6)
        # 创建各个排列选项
        sortStuID = ttk.Radiobutton(sortOption, text="学号", variable=sortType, value=0, command=updateRank)
        sortStuID.place(relx=0, rely=0, relwidth=1/6, relheight=1)
        sortChinese = ttk.Radiobutton(sortOption, text="语文", variable=sortType, value=1, command=updateRank)
        sortChinese.place(relx=1/6, rely=0, relwidth=1/6, relheight=1)
        sortMath = ttk.Radiobutton(sortOption, text="数学", variable=sortType, value=2, command=updateRank)
        sortMath.place(relx=2/6, rely=0, relwidth=1/6, relheight=1)
        sortEnglish = ttk.Radiobutton(sortOption, text="英语", variable=sortType, value=3, command=updateRank)
        sortEnglish.place(relx=3/6, rely=0, relwidth=1/6, relheight=1)
        sortTotal = ttk.Radiobutton(sortOption, text="总分", variable=sortType, value=4, command=updateRank)
        sortTotal.place(relx=4/6, rely=0, relwidth=1/6, relheight=1)
        optSort = ttk.Checkbutton(sortOption, text="正序", variable=isSort, onvalue=True, offvalue=False,
                                  command=updateRank)
        optSort.place(relx=5/6, rely=0, relwidth=1/6, relheight=1)

        formFrame = ttk.Frame(viewStudent)
        formFrame.place(relx=0, rely=1/6, relwidth=1, relheight=5/6)
        studentForm = ttk.Treeview(formFrame, show="headings",
                                   columns=("排名", "学号", "姓名", "性别", "语文", "数学", "英语", "总分"),
                                   selectmode="extended")
        studentForm.column("排名", width=5, anchor="center")
        studentForm.column("学号", width=5, anchor="center")
        studentForm.column("姓名", width=6, anchor="center")
        studentForm.column("性别", width=5, anchor="center")
        studentForm.column("语文", width=3, anchor="center")
        studentForm.column("数学", width=3, anchor="center")
        studentForm.column("英语", width=3, anchor="center")
        studentForm.column("总分", width=3, anchor="center")

        studentForm.heading("排名", text="排名")
        studentForm.heading("学号", text="学号")
        studentForm.heading("姓名", text="姓名")
        studentForm.heading("性别", text="性别")
        studentForm.heading("语文", text="语文成绩")
        studentForm.heading("数学", text="数学成绩")
        studentForm.heading("英语", text="英语成绩")
        studentForm.heading("总分", text="总分")
        studentForm.place(relx=0, rely=0, relwidth=1, relheight=1)

        updateRank()
        viewStudent.mainloop()

    def __modifyStudent(self):  # 修改某位学生的信息
        option = sdialog.askinteger("修改学生信息", "请输入要修改的学生学号", parent=self.main)
        if option != None:
            try:
                ID = option
                name = students[option][0]
                gender = students[option][1]
                chinese = students[option][2]
                math = students[option][3]
                english = students[option][4]
            except KeyError:
                msgbox.showerror("错误", "学号不存在")
            else:
                def close():
                    try:
                        int(stuID.get())
                    except ValueError:
                        msgbox.showerror("错误", "新学号非数字")
                    else:
                        if self.__issame(int(stuID.get())) and int(stuID.get()) != ID:
                            msgbox.showerror("错误", "新学号重复")
                        else:
                            score = [self.__getscore(stuChinese.get(), "语文"), self.__getscore(
                                stuMath.get(), "数学"), self.__getscore(stuEnglish.get(), "英语")]
                            if -1 not in score:
                                students[int(stuID.get())] = [stuName.get(), stuGender.get(),
                                                              float(stuChinese.get()), float(stuMath.get()),
                                                              float(stuEnglish.get())]
                                self.state = "modified"
                    modify.destroy()
                modify = tk.Toplevel(self.main)
                modify.title("修改学生信息")
                modify.geometry("600x300")
                modify.protocol("WM_DELETE_WINDOW", close)
                ttk.Label(modify, text="学号").place(relx=0, rely=0, relwidth=1/4, relheight=1/3)
                stuID = ttk.Entry(modify)
                stuID.place(relx=1/4, rely=0, relwidth=1/4, relheight=1/3)
                stuID.insert(0, ID)
                ttk.Label(modify, text="姓名").place(relx=2/4, rely=0, relwidth=1/4, relheight=1/3)
                stuName = ttk.Entry(modify)
                stuName.place(relx=3/4, rely=0, relwidth=1/4, relheight=1/3)
                stuName.insert(0, name)
                ttk.Label(modify, text="性别").place(relx=0, rely=1/3, relwidth=1/4, relheight=1/3)
                stuGender = ttk.Entry(modify)
                stuGender.place(relx=1/4, rely=1/3, relwidth=1/4, relheight=1/3)
                stuGender.insert(0, gender)
                ttk.Label(modify, text="语文成绩").place(relx=2/4, rely=1/3, relwidth=1/4, relheight=1/3)
                stuChinese = ttk.Entry(modify)
                stuChinese.place(relx=3/4, rely=1/3, relwidth=1/4, relheight=1/3)
                stuChinese.insert(0, chinese)
                ttk.Label(modify, text="数学成绩").place(relx=0, rely=2/3, relwidth=1/4, relheight=1/3)
                stuMath = ttk.Entry(modify)
                stuMath.place(relx=1/4, rely=2/3, relwidth=1/4, relheight=1/3)
                stuMath.insert(0, math)
                ttk.Label(modify, text="英语成绩").place(relx=2/4, rely=2/3, relwidth=1/4, relheight=1/3)
                stuEnglish = ttk.Entry(modify)
                stuEnglish.place(relx=3/4, rely=2/3, relwidth=1/4, relheight=1/3)
                stuEnglish.insert(0, english)
                modify.mainloop()

    def __addStudent(self):  # 添加学生
        def close():
            global students
            try:
                int(stuID.get())
            except ValueError:
                msgbox.showerror("错误", "学号非数字")
            else:
                if self.__issame(int(stuID.get())):
                    msgbox.showerror("错误", "学号重复")
                else:
                    score = [self.__getscore(stuChinese.get(), "语文"), self.__getscore(stuMath.get(), "数学"),
                             self.__getscore(stuEnglish.get(), "英语")]
                    if -1 not in score:
                        students[int(stuID.get())] = [stuName.get(), stuGender.get(), float(stuChinese.get()),
                                                      float(stuMath.get()), float(stuEnglish.get())]
                        # 按学号排序
                        students = dict(sorted(students.items(), key=lambda x: x[0]))
                        self.state = "modified"
            add.destroy()

        add = tk.Toplevel(self.main)
        add.title("添加学生信息")
        add.geometry("600x300")
        add.protocol("WM_DELETE_WINDOW", close)
        ttk.Label(add, text="学号").place(relx=0, rely=0, relwidth=1/4, relheight=1/3)
        stuID = ttk.Entry(add)
        stuID.place(relx=1/4, rely=0, relwidth=1/4, relheight=1/3)
        ttk.Label(add, text="姓名").place(relx=2/4, rely=0, relwidth=1/4, relheight=1/3)
        stuName = ttk.Entry(add)
        stuName.place(relx=3/4, rely=0, relwidth=1/4, relheight=1/3)
        ttk.Label(add, text="性别").place(relx=0, rely=1/3, relwidth=1/4, relheight=1/3)
        stuGender = ttk.Entry(add)
        stuGender.place(relx=1/4, rely=1/3, relwidth=1/4, relheight=1/3)
        ttk.Label(add, text="语文成绩").place(relx=2/4, rely=1/3, relwidth=1/4, relheight=1/3)
        stuChinese = ttk.Entry(add)
        stuChinese.place(relx=3/4, rely=1/3, relwidth=1/4, relheight=1/3)
        ttk.Label(add, text="数学成绩").place(relx=0, rely=2/3, relwidth=1/4, relheight=1/3)
        stuMath = ttk.Entry(add)
        stuMath.place(relx=1/4, rely=2/3, relwidth=1/4, relheight=1/3)
        ttk.Label(add, text="英语成绩").place(relx=2/4, rely=2/3, relwidth=1/4, relheight=1/3)
        stuEnglish = ttk.Entry(add)
        stuEnglish.place(relx=3/4, rely=2/3, relwidth=1/4, relheight=1/3)

        add.mainloop()

    def __queryStudent(self):  # 查询某位学生的信息
        query = tk.Toplevel(self.main)
        query.title("查询学生信息")
        query.geometry("600x100")
        ttk.Label(query, text="学号").place(relx=0, rely=0, relwidth=1/3, relheight=1)
        stuID = ttk.Entry(query)
        stuID.place(relx=1/3, rely=0, relwidth=1/3, relheight=1)

        def queryStudent():
            try:
                name = students[int(stuID.get())][0]
                gender = students[int(stuID.get())][1]
                chinese = students[int(stuID.get())][2]
                math = students[int(stuID.get())][3]
                english = students[int(stuID.get())][4]
                msgbox.showinfo("查询结果", f"学号：{stuID.get()}\n姓名：{name}\n性别：{gender}"
                                f"\n语文成绩：{chinese}\n数学成绩：{math}\n英语成绩：{english}")
            except KeyError:
                msgbox.showerror("错误", "学号不存在")
            except ValueError:
                msgbox.showerror("错误", "学号非数字")

        ttk.Button(query, text="查询", command=queryStudent).place(relx=2/3, rely=0, relwidth=1/3, relheight=1)

        query.mainloop()

    def __deleteStudent(self):  # 删除学生信息
        def close():
            global students
            try:
                del students[int(stuID.get())]
            except KeyError:
                msgbox.showerror("错误", "学号不存在")
            except ValueError:
                msgbox.showerror("错误：学号非数字")
            else:
                # 按学号排序
                students = dict(sorted(students.items(), key=lambda x: x[0]))
                self.state = "modified"
            delete.destroy()

        delete = tk.Toplevel(self.main)
        delete.title("删除学生信息")
        delete.geometry("600x100")
        delete.protocol("WM_DELETE_WINDOW", close)
        ttk.Label(delete, text="学号").place(relx=0, rely=0, relwidth=1/2, relheight=1)
        stuID = ttk.Entry(delete)
        stuID.place(relx=1/2, rely=0, relwidth=1/2, relheight=1)

        delete.mainloop()

    def __generateButton(self, name, command, x, y, /):  # 生成按钮
        ttk.Button(self.main, text=name, command=command).place(relx=(x-1)/3, rely=y/3,
                                                                relwidth=1/3, relheight=1/3)

    def __issame(self, id):  # 判断学生ID是否相同
        for i in students:
            if i == id:
                return True
        return False

    def __closeWindow(self):  # 关闭主窗口
        if self.state not in ("new", "loaded"):
            option = msgbox.askyesnocancel("保存", "保存对此信息做出的更改？")
            if option:
                self.__save()
            elif not option and option != None:
                students.clear()
                self.state = "new"
        self.main.destroy()

    def __getscore(self, score, subject):  # 分数判断
        try:
            float(score)
        except:
            msgbox.showerror("错误", f"{subject}成绩非数字")
            return -1
        if float(score) < 0 or float(score) > 100:
            msgbox.showerror("错误", f"{subject}成绩有误")
            return -1
        return float(score)


Main()
