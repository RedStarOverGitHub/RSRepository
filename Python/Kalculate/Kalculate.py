import sys
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QTabWidget, QPushButton, QLabel,
                              QListWidget, QMenuBar, QMenu, QGridLayout,
                              QLineEdit, QMessageBox, QFileDialog, QSplitter,
                              QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')

class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 加载UI文件
        loader = QUiLoader()
        self.ui = loader.load("qtUI.ui", self)
        self.setCentralWidget(self.ui)

        # 初始化符号变量
        self.x, self.y, self.z = sp.symbols('x y z')
        self.current_expression = ""
        self.history = []
        self.transformations = standard_transformations + (implicit_multiplication_application,)

        # 角度制设置，默认为弧度制
        self.angle_mode = "RAD" 

        # 2nd键状态，用于控制按键功能切换
        self.second_mode = {
            "basic_tab": False,
            "tab_alge": False, 
            "trigo_tab": False,
            "calcu_tab": False,
            "tab_stat": False,
            "tab_marset": False,
            "tab_char": False
        }

        # 连接UI元素和信号
        self.setup_ui_connections()

    def setup_ui_connections(self):
        """设置UI元素和连接信号"""
        # 输入框
        self.expression_input = self.ui.lineEdit
        self.expression_input.textChanged.connect(self.on_expression_changed)
        self.expression_input.returnPressed.connect(self.calculate)

        # LaTeX显示视图初始化
        self.web_view = self.ui.webEngineView
        self.web_view.setHtml("<html><body></body></html>")

        # 连接所有标签页的切换信号
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)

        # 连接所有按钮
        self.connect_all_buttons()

        # 显示主窗口
        self.show()

    def get_empty_latex_html(self):
        """返回空的LaTeX HTML"""
        return "<html><body></body></html>"

    def connect_all_buttons(self):
        """连接所有按钮"""
        # 遍历所有标签页
        for i in range(self.ui.tabWidget.count()):
            tab = self.ui.tabWidget.widget(i)
            tab_name = tab.objectName()

            # 连接该标签页的所有按钮
            for btn in tab.findChildren(QPushButton):
                # 2nd按钮特殊处理
                if "2nd" in btn.objectName():
                    btn.clicked.connect(lambda checked=False, t=tab_name: self.toggle_second_mode(t))
                else:
                    # 其他按钮连接到通用处理函数
                    btn.clicked.connect(lambda checked=False, button=btn: self.on_button_clicked(button))

    def toggle_second_mode(self, tab_name):
        """切换指定标签页的2nd模式"""
        # 切换状态
        self.second_mode[tab_name] = not self.second_mode[tab_name]

        # 更新按钮显示
        self.update_buttons_for_second_mode(tab_name)

    def update_buttons_for_second_mode(self, tab_name):
        """根据2nd模式状态更新按钮显示和功能"""
        # 获取当前标签页
        tab = getattr(self.ui, tab_name)

        # 获取2nd按钮并高亮显示
        second_buttons = {
            "basic_tab": "pushButton_ans",  # 基本页没有专门的2nd按钮，临时用这个
            "tab_alge": "pushButton_2nda",
            "trigo_tab": "pushButton_2ndt",
            "calcu_tab": "pushButton_2ndc",
            "tab_stat": "pushButton_2nds",
            "tab_marset": "pushButton_2ndms",
            "tab_char": "pushButton_2ndch"
        }

        # 如果存在2nd按钮，高亮显示
        if tab_name in second_buttons and hasattr(self.ui, second_buttons[tab_name]):
            second_btn = getattr(self.ui, second_buttons[tab_name])
            if self.second_mode[tab_name]:
                second_btn.setStyleSheet("background-color: lightblue;")
            else:
                second_btn.setStyleSheet("")

        # 根据不同标签页执行特定更新
        if tab_name == "basic_tab":
            self.update_basic_tab_buttons()
        elif tab_name == "tab_alge":
            self.update_algebra_tab_buttons()
        elif tab_name == "trigo_tab":
            self.update_trig_tab_buttons()
        elif tab_name == "calcu_tab":
            self.update_calculus_tab_buttons()
        elif tab_name == "tab_stat":
            self.update_stats_tab_buttons()
        elif tab_name == "tab_marset":
            self.update_matrix_tab_buttons()
        elif tab_name == "tab_char":
            self.update_character_tab_buttons()

    def update_basic_tab_buttons(self):
        """更新基本标签页按钮"""
        is_second = self.second_mode["basic_tab"]

        # 示例: 在2nd模式下修改某些按钮
        button_changes = {
            "pushButton_log": ("log", "ln"),
            "pushButton_root": ("√", "x²")
        }

        for btn_name, (normal, second) in button_changes.items():
            if hasattr(self.ui, btn_name):
                btn = getattr(self.ui, btn_name)
                btn.setText(second if is_second else normal)

    def update_algebra_tab_buttons(self):
        """更新代数标签页按钮"""
        is_second = self.second_mode["tab_alge"]

        # 代数页面按钮变化
        button_changes = {
            "pushButton_cefl": ("⌈a⌉", "⌊a⌋"),  # 上取整变下取整
            "pushButton_gidp": ("[a]", "‖a‖")   # 最近整数变范数
        }

        for btn_name, (normal, second) in button_changes.items():
            if hasattr(self.ui, btn_name):
                btn = getattr(self.ui, btn_name)
                btn.setText(second if is_second else normal)

    def update_trig_tab_buttons(self):
        """更新三角函数标签页按钮"""
        is_second = self.second_mode["trigo_tab"]

        # 三角函数变为反三角函数
        button_changes = {
            "pushButton_sin": ("sin", "asin"),
            "pushButton_cos": ("cos", "acos"),
            "pushButton_tan": ("tan", "atan"),
            "pushButton_cot": ("cot", "acot"),
            "pushButton_sec": ("sec", "asec"),
            "pushButton_csc": ("csc", "acsc")
        }

        for btn_name, (normal, second) in button_changes.items():
            if hasattr(self.ui, btn_name):
                btn = getattr(self.ui, btn_name)
                btn.setText(second if is_second else normal)

    def update_calculus_tab_buttons(self):
        """更新微积分标签页按钮"""
        is_second = self.second_mode["calcu_tab"]

        # 微积分按钮变化
        button_changes = {
            "pushButton_diff": ("'", "∂"),      # 普通导数变偏导数
            "pushButton_inter": ("∫", "∬"),     # 一重积分变二重积分
            "pushButton_lim": ("lim", "lim_{∞}") # 普通极限变无穷极限
        }

        for btn_name, (normal, second) in button_changes.items():
            if hasattr(self.ui, btn_name):
                btn = getattr(self.ui, btn_name)
                btn.setText(second if is_second else normal)

    def update_stats_tab_buttons(self):
        """更新统计标签页按钮"""
        is_second = self.second_mode["tab_stat"]

        # 统计按钮变化
        button_changes = {
            "pushButton_mea": ("x̅", "E(X)"),    # 样本均值变期望
            "pushButton_vari": ("σ", "σ²")      # 标准差变方差
        }

        for btn_name, (normal, second) in button_changes.items():
            if hasattr(self.ui, btn_name):
                btn = getattr(self.ui, btn_name)
                btn.setText(second if is_second else normal)

    def update_matrix_tab_buttons(self):
        """更新矩阵标签页按钮"""
        is_second = self.second_mode["tab_marset"]

        # 矩阵/集合按钮变化
        button_changes = {
            "pushButton_lsb": ("[", "⟨"),      # 方括号变尖括号
            "pushButton_rsb": ("]", "⟩"),
            "pushButton_Pm": ("P", "det")      # 排列变行列式
        }

        for btn_name, (normal, second) in button_changes.items():
            if hasattr(self.ui, btn_name):
                btn = getattr(self.ui, btn_name)
                btn.setText(second if is_second else normal)

    def update_character_tab_buttons(self):
        """更新字符标签页按钮"""
        is_second = self.second_mode["tab_char"]

        # 更新小写字母为大写字母
        for letter in "abcdefghijklmnopqrstuvwxyz":
            btn_name = f"pushButton_{letter}"
            if hasattr(self.ui, btn_name):
                btn = getattr(self.ui, btn_name)
                btn.setText(letter.upper() if is_second else letter)

        # 更新希腊字母为大写
        greek_letters = {
            "alph": ("α", "Α"),
            "beta": ("β", "Β"),
            "gama": ("γ", "Γ"),
            "delt": ("δ", "Δ"),
            "epsi": ("ε", "Ε"),
            "zeta": ("ζ", "Ζ"),
            "eta": ("η", "Η"),
            "thet": ("θ", "Θ"),
            "iota": ("ι", "Ι"),
            "kapa": ("κ", "Κ"),
            "lamd": ("λ", "Λ"),
            "mu": ("μ", "Μ"),
            "nu": ("ν", "Ν"),
            "ksi": ("ξ", "Ξ"),
            "omic": ("ο", "Ο"),
            "pi": ("π", "Π"),
            "rho": ("ρ", "Ρ"),
            "sigm": ("σ", "Σ"),
            "tau": ("τ", "Τ"),
            "upsi": ("υ", "Υ"),
            "phi": ("φ", "Φ"),
            "chi": ("χ", "Χ"),
            "psi": ("ψ", "Ψ"),
            "omeg": ("ω", "Ω")
        }

        for name, (lower, upper) in greek_letters.items():
            btn_name = f"pushButton_{name}"
            if hasattr(self.ui, btn_name):
                btn = getattr(self.ui, btn_name)
                btn.setText(upper if is_second else lower)

        # 更新特殊符号
        symbol_changes = {
            "pushButton_sym1": ("∞", "⊥"),
            "pushButton_sym2": ("z̄", "‖"),
            "pushButton_sym3": ("%", "♯"),
            "pushButton_sym4": ("mod", "♭"),
            "pushButton_sym5": ("∂", "♮"),
            "pushButton_sym6": ("!", "♦"),
            "pushButton_sym7": ("a/b", "♣"),
            "pushButton_sym8": ("°", "♠")
        }

        for btn_name, (normal, second) in symbol_changes.items():
            if hasattr(self.ui, btn_name):
                btn = getattr(self.ui, btn_name)
                btn.setText(second if is_second else normal)

    def on_button_clicked(self, button):
        """按钮点击事件处理"""
        # 获取按钮文本
        text = button.text()

        # 当前标签页
        current_tab = self.ui.tabWidget.currentWidget().objectName()
        is_second = self.second_mode.get(current_tab, False)

        # 数字和基本运算符
        if text in '0123456789.':
            self.add_to_expression(text)
        elif text in '+-*/()=<>≤≥≠':
            # 运算符直接添加
            self.add_to_expression(text)
        # 特殊符号和常数
        elif text == 'π':
            self.add_to_expression('pi')
        elif text == 'e':
            self.add_to_expression('e')
        elif text == 'i':
            self.add_to_expression('I')  # sympy使用I表示虚数单位
        # 基本函数
        elif text == '√':
            self.add_function("sqrt({})")
        elif text == 'x²':  # 2nd模式下的平方
            self.add_function("({})**2")
        elif text == '^' or text == '**':
            self.add_to_expression('**')
        elif text == 'log':
            self.add_function("log({}, 10)")  # 以10为底的对数
        elif text == 'ln':  # 2nd模式下的自然对数
            self.add_function("log({})")  # 默认以e为底
        # 三角函数和反三角函数
        elif text in ['sin', 'cos', 'tan', 'cot', 'sec', 'csc',
                     'asin', 'acos', 'atan', 'acot', 'asec', 'acsc']:
            self.add_function(f"{text}({{}})")
        # 微积分操作
        elif text == "'":  # 导数
            self.calculate_derivative()
        elif text == '∂':  # 偏导数
            self.calculate_partial_derivative()
        elif text == '∫':  # 积分
            self.calculate_integral()
        elif text == '∬':  # 二重积分
            self.calculate_double_integral()
        elif text == 'lim':  # 极限
            self.add_function("limit({}, x, 0)")
        # 代数操作
        elif text == 'Factor':
            self.apply_operation(sp.factor)
        elif text == 'Expend':
            self.apply_operation(sp.expand)
        elif text == 'Simplify':
            self.apply_operation(sp.simplify)
        elif text == 'Solve':
            self.solve_equation()
        # 统计函数
        elif text == 'x̅':  # 平均值
            self.calculate_mean()
        elif text == 'x̃':  # 中位数
            self.calculate_median()
        elif text == 'σ':  # 标准差
            self.calculate_std()
        elif text == 'σ²':  # 方差
            self.calculate_variance()
        # 矩阵/集合运算
        elif text in '[]{}⟨⟩|∈∩∪\⊂⊃⊆⊇∀∃△∅#':
            # 特殊字符直接添加到表达式
            self.add_to_expression(text)
        # 字母按钮 - 直接添加到表达式
        else:
            # 特殊转换为sympy识别的符号
            sympy_replacements = {
                'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta',
                'ε': 'epsilon', 'ζ': 'zeta', 'η': 'eta', 'θ': 'theta',
                'ι': 'iota', 'κ': 'kappa', 'λ': 'lambda', 'μ': 'mu',
                'ν': 'nu', 'ξ': 'xi', 'ο': 'omicron', 'π': 'pi',
                'ρ': 'rho', 'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon',
                'φ': 'phi', 'χ': 'chi', 'ψ': 'psi', 'ω': 'omega',
                # 大写希腊字母
                'Α': 'Alpha', 'Β': 'Beta', 'Γ': 'Gamma', 'Δ': 'Delta',
                'Ε': 'Epsilon', 'Ζ': 'Zeta', 'Η': 'Eta', 'Θ': 'Theta',
                'Ι': 'Iota', 'Κ': 'Kappa', 'Λ': 'Lambda', 'Μ': 'Mu',
                'Ν': 'Nu', 'Ξ': 'Xi', 'Ο': 'Omicron', 'Π': 'Pi',
                'Ρ': 'Rho', 'Σ': 'Sigma', 'Τ': 'Tau', 'Υ': 'Upsilon',
                'Φ': 'Phi', 'Χ': 'Chi', 'Ψ': 'Psi', 'Ω': 'Omega'
            }

            if text in sympy_replacements:
                self.add_to_expression(sympy_replacements[text])
            else:
                # 其他字符直接添加
                self.add_to_expression(text)

    def add_function(self, template):
        """添加函数模板，保留光标在括号内"""
        cursor_pos = self.expression_input.cursorPosition()
        selected_text = self.expression_input.selectedText()

        if selected_text:
            # 如果有选中文本，将其放入函数中
            new_text = template.format(selected_text)
            self.current_expression = (
                self.current_expression[:self.expression_input.selectionStart()] +
                new_text +
                self.current_expression[self.expression_input.selectionEnd():]
            )
            new_cursor_pos = self.expression_input.selectionStart() + len(new_text)
        else:
            # 如果没有选中文本，插入函数并将光标置于括号内
            # 找到{}占位符的位置
            placeholder_pos = template.find("{}")
            if placeholder_pos != -1:
                # 插入带空括号的函数
                function_text = template.replace("{}", "")
                self.current_expression = (
                    self.current_expression[:cursor_pos] +
                    function_text +
                    self.current_expression[cursor_pos:]
                )
                # 光标位置为函数名后的括号内
                new_cursor_pos = cursor_pos + placeholder_pos
            else:
                # 如果没有{}占位符，直接添加函数
                self.current_expression = (
                    self.current_expression[:cursor_pos] +
                    template +
                    self.current_expression[cursor_pos:]
                )
                new_cursor_pos = cursor_pos + len(template)

        # 更新UI
        self.expression_input.setText(self.current_expression)
        self.expression_input.setCursorPosition(new_cursor_pos)
        self.update_input_latex_display()

    def calculate_partial_derivative(self):
        """计算偏导数"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            # 弹出对话框获取变量
            var_name, ok = QMessageBox.question(self, "偏导数", 
                                               "选择变量:
[是] - 对x求偏导
[否] - 对y求偏导",
                                               QMessageBox.Yes | QMessageBox.No)

            if not ok:
                return

            var = self.x if var_name == QMessageBox.Yes else self.y

            # 解析表达式
            expr = parse_expr(self.current_expression,
                             local_dict={'x': self.x, 'y': self.y, 'z': self.z},
                             transformations=self.transformations)

            # 计算偏导数
            result = sp.diff(expr, var)

            # 更新表达式和显示
            var_symbol = 'x' if var == self.x else 'y'
            self.current_expression = f"∂({self.current_expression})/∂{var_symbol} = {result}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()

            # 更新LaTeX结果
            latex_result = sp.latex(result)
            self.update_result_latex_display(latex_result)

        except Exception as e:
            QMessageBox.critical(self, "偏导数错误", f"错误: {str(e)}")

    def calculate_double_integral(self):
        """计算二重积分"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            # 解析表达式
            expr = parse_expr(self.current_expression,
                             local_dict={'x': self.x, 'y': self.y},
                             transformations=self.transformations)

            # 先对x积分
            integral_x = sp.integrate(expr, self.x)

            # 再对y积分
            result = sp.integrate(integral_x, self.y)

            # 更新表达式和显示
            self.current_expression = f"∬{self.current_expression}dxdy = {result}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()

            # 更新LaTeX结果
            latex_result = sp.latex(result)
            self.update_result_latex_display(latex_result)

        except Exception as e:
            QMessageBox.critical(self, "二重积分错误", f"错误: {str(e)}")

    def calculate_gcd(self):
        """计算最大公约数"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析输入数据为整数列表
            data = [int(float(x)) for x in data_str.split(",")]

            # 使用sympy计算最大公约数
            result = data[0]
            for num in data[1:]:
                result = sp.gcd(result, num)

            # 显示结果
            self.current_expression = f"GCD({data_str}) = {result}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display(str(result))

        except Exception as e:
            QMessageBox.critical(self, "GCD错误", f"错误: {str(e)}")

    def calculate_lcm(self):
        """计算最小公倍数"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析输入数据为整数列表
            data = [int(float(x)) for x in data_str.split(",")]

            # 使用sympy计算最小公倍数
            result = data[0]
            for num in data[1:]:
                result = sp.lcm(result, num)

            # 显示结果
            self.current_expression = f"LCM({data_str}) = {result}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display(str(result))

        except Exception as e:
            QMessageBox.critical(self, "LCM错误", f"错误: {str(e)}")

    def calculate_max(self):
        """计算最大值"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析输入数据
            data = [float(x) for x in data_str.split(",")]
            max_value = max(data)

            # 显示结果
            self.current_expression = f"Max({data_str}) = {max_value}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display(str(max_value))

        except Exception as e:
            QMessageBox.critical(self, "Max错误", f"错误: {str(e)}")

    def calculate_min(self):
        """计算最小值"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析输入数据
            data = [float(x) for x in data_str.split(",")]
            min_value = min(data)

            # 显示结果
            self.current_expression = f"Min({data_str}) = {min_value}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display(str(min_value))

        except Exception as e:
            QMessageBox.critical(self, "Min错误", f"错误: {str(e)}")

    def insert_answer(self):
        """插入上一个计算结果"""
        if self.history:
            # 获取最后一个计算结果
            last_result = self.history[-1].split("=")[-1].strip()
            self.add_to_expression(last_result)

    def insert_sqrt(self):
        """插入平方根函数"""
        self.add_function("sqrt({})")

    def insert_log(self):
        """插入对数函数"""
        # 根据当前2nd模式决定是ln还是log
        current_tab = self.ui.tabWidget.currentWidget().objectName()
        if self.second_mode.get(current_tab, False):
            # 自然对数(ln)
            self.add_function("log({})")
        else:
            # 常用对数(log10)
            self.add_function("log({}, 10)")

    def insert_trig_function(self, func_name):
        """插入三角函数"""
        # 获取当前标签页和2nd状态
        current_tab = self.ui.tabWidget.currentWidget().objectName()
        is_second = self.second_mode.get(current_tab, False)

        # 根据2nd状态决定是三角函数还是反三角函数
        if is_second:
            func = "a" + func_name
        else:
            func = func_name

        self.add_function(f"{func}({{}})")

    def insert_special_function(self, func_name):
        """插入特殊函数"""
        func_templates = {
            "Si": "Si({})",      # 正弦积分
            "Ci": "Ci({})",      # 余弦积分
            "li": "li({})",      # 对数积分
            "O": "O({})",        # 大O符号
            "Sum": "Sum({}, (i, 0, n))"  # 求和符号
        }

        if func_name in func_templates:
            self.add_function(func_templates[func_name])
        else:
            self.add_function(f"{func_name}({{}})")

    def toggle_hyperbolic(self):
        """切换双曲函数模式"""
        # 获取当前标签页
        current_tab = "trigo_tab"

        # 检查当前是否为双曲模式
        hyp_button = self.ui.pushButton_hyp
        is_hyp_mode = hyp_button.styleSheet() != ""

        # 切换双曲模式
        if is_hyp_mode:
            hyp_button.setStyleSheet("")
            # 恢复正常三角函数
            if hasattr(self.ui, "pushButton_sin"):
                self.ui.pushButton_sin.setText("sin")
            if hasattr(self.ui, "pushButton_cos"):
                self.ui.pushButton_cos.setText("cos")
            if hasattr(self.ui, "pushButton_tan"):
                self.ui.pushButton_tan.setText("tan")
        else:
            hyp_button.setStyleSheet("background-color: lightgreen;")
            # 切换为双曲函数
            if hasattr(self.ui, "pushButton_sin"):
                self.ui.pushButton_sin.setText("sinh")
            if hasattr(self.ui, "pushButton_cos"):
                self.ui.pushButton_cos.setText("cosh")
            if hasattr(self.ui, "pushButton_tan"):
                self.ui.pushButton_tan.setText("tanh")

    def toggle_sign(self):
        """切换正负号"""
        # 获取当前表达式
        expr = self.current_expression
        cursor_pos = self.expression_input.cursorPosition()

        # 找到光标所在位置的数字
        # 向左搜索数字的起始位置
        start = cursor_pos
        while start > 0 and (expr[start-1].isdigit() or expr[start-1] == '.'):
            start -= 1

        # 检查数字前是否有负号
        if start > 0 and expr[start-1] == '-':
            # 有负号，移除负号
            self.current_expression = expr[:start-1] + expr[start:]
            self.expression_input.setText(self.current_expression)
            self.expression_input.setCursorPosition(cursor_pos - 1)
        else:
            # 没有负号，添加负号
            self.current_expression = expr[:start] + '-' + expr[start:]
            self.expression_input.setText(self.current_expression)
            self.expression_input.setCursorPosition(cursor_pos + 1)

        self.update_input_latex_display()

    def wrap_expression(self, func_name):
        """包装表达式，如abs(), ceiling()等"""
        self.add_function(f"{func_name}({{}})")

    
    def calculate_partial_derivative(self):
        """计算偏导数 - 2nd模式下的导数功能"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            # 询问用户要对哪个变量求偏导
            var_name, ok = QInputDialog.getText(self, "偏导数", "对哪个变量求偏导数? (默认为x)")
            if ok:
                if not var_name:
                    var_name = 'x'

                var = sp.Symbol(var_name)
                expr = parse_expr(self.current_expression, 
                                  local_dict={'x': self.x, 'y': self.y, 'z': self.z},
                                  transformations=self.transformations)
                derivative = sp.diff(expr, var)

                result = f"∂({self.current_expression})/∂{var_name} = {derivative}"
                self.expression_input.setText(result)
                self.current_expression = result
                self.update_input_latex_display()

                # 添加到历史
                self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "偏导数错误", f"错误: {str(e)}")

    def calculate_double_integral(self):
        """计算二重积分 - 2nd模式下的积分功能"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            # 询问用户积分变量和区间
            var1_name, ok1 = QInputDialog.getText(self, "二重积分", "第一个积分变量? (默认为x)")
            if not ok1:
                return

            var1_name = var1_name if var1_name else 'x'
            var1 = sp.Symbol(var1_name)

            var2_name, ok2 = QInputDialog.getText(self, "二重积分", "第二个积分变量? (默认为y)")
            if not ok2:
                return

            var2_name = var2_name if var2_name else 'y'
            var2 = sp.Symbol(var2_name)

            # 解析表达式
            expr = parse_expr(self.current_expression,
                             local_dict={'x': self.x, 'y': self.y, 'z': self.z},
                             transformations=self.transformations)

            # 计算二重积分 (无界积分)
            double_integral = sp.integrate(sp.integrate(expr, var1), var2)

            result = f"∬{self.current_expression} d{var1_name}d{var2_name} = {double_integral} + C"
            self.expression_input.setText(result)
            self.current_expression = result
            self.update_input_latex_display()

            # 添加到历史
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "二重积分错误", f"错误: {str(e)}")

    def insert_special_function(self, func_name):
        """插入特殊函数"""
        if func_name == "Si":
            self.add_function("Si({})")  # 正弦积分
        elif func_name == "Ci":
            self.add_function("Ci({})")  # 余弦积分
        elif func_name == "li":
            self.add_function("li({})")  # 对数积分
        elif func_name == "O":
            self.add_function("O({})")  # 大O记号
        elif func_name == "Sum":
            self.add_function("Sum({}, (i, 0, n))")  # 求和

    def insert_sqrt(self):
        """插入平方根函数"""
        # 检查是否在2nd模式
        current_tab = self.ui.tabWidget.currentWidget().objectName()
        is_second = self.second_mode.get(current_tab, False)

        if is_second:
            # 在2nd模式下插入平方
            self.add_function("({})**2")
        else:
            # 正常模式下插入平方根
            self.add_function("sqrt({})")

    def insert_log(self):
        """插入对数函数"""
        # 检查是否在2nd模式
        current_tab = self.ui.tabWidget.currentWidget().objectName()
        is_second = self.second_mode.get(current_tab, False)

        if is_second:
            # 在2nd模式下插入自然对数
            self.add_function("log({})")  # 默认以e为底
        else:
            # 正常模式下插入常用对数
            self.add_function("log({}, 10)")  # 以10为底

    def insert_trig_function(self, func_name):
        """插入三角函数"""
        # 检查是否在2nd模式
        current_tab = self.ui.tabWidget.currentWidget().objectName()
        is_second = self.second_mode.get(current_tab, False)

        # 检查是否在双曲模式
        hyperbolic = hasattr(self, "hyperbolic_mode") and self.hyperbolic_mode

        if is_second:
            # 在2nd模式下为反三角函数
            if hyperbolic:
                # 反双曲函数
                self.add_function(f"a{func_name}h({{}})")
            else:
                # 反三角函数
                self.add_function(f"a{func_name}({{}})")
        else:
            if hyperbolic:
                # 双曲函数
                self.add_function(f"{func_name}h({{}})")
            else:
                # 普通三角函数
                self.add_function(f"{func_name}({{}})")

    def toggle_hyperbolic(self):
        """切换双曲函数模式"""
        if not hasattr(self, "hyperbolic_mode"):
            self.hyperbolic_mode = False

        self.hyperbolic_mode = not self.hyperbolic_mode

        # 设置按钮高亮
        if hasattr(self.ui, "pushButton_hyp"):
            if self.hyperbolic_mode:
                self.ui.pushButton_hyp.setStyleSheet("background-color: lightgreen;")
            else:
                self.ui.pushButton_hyp.setStyleSheet("")

    def calculate_gcd(self):
        """计算最大公约数"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析输入数据
            data = [int(x) for x in data_str.split(",")]

            # 使用sympy计算最大公约数
            gcd_result = data[0]
            for i in range(1, len(data)):
                gcd_result = sp.gcd(gcd_result, data[i])

            # 显示结果
            result = f"GCD: {gcd_result}"
            self.expression_input.setText(result)
            self.current_expression = result
            self.update_input_latex_display()

            # 添加到历史
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "GCD错误", f"错误: {str(e)}")

    def calculate_lcm(self):
        """计算最小公倍数"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析输入数据
            data = [int(x) for x in data_str.split(",")]

            # 使用sympy计算最小公倍数
            lcm_result = data[0]
            for i in range(1, len(data)):
                lcm_result = sp.lcm(lcm_result, data[i])

            # 显示结果
            result = f"LCM: {lcm_result}"
            self.expression_input.setText(result)
            self.current_expression = result
            self.update_input_latex_display()

            # 添加到历史
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "LCM错误", f"错误: {str(e)}")

    def calculate_max(self):
        """计算最大值"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析输入数据
            data = [float(x) for x in data_str.split(",")]
            max_value = max(data)

            # 显示结果
            result = f"Max: {max_value}"
            self.expression_input.setText(result)
            self.current_expression = result
            self.update_input_latex_display()

            # 添加到历史
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "Max错误", f"错误: {str(e)}")

    def calculate_min(self):
        """计算最小值"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析输入数据
            data = [float(x) for x in data_str.split(",")]
            min_value = min(data)

            # 显示结果
            result = f"Min: {min_value}"
            self.expression_input.setText(result)
            self.current_expression = result
            self.update_input_latex_display()

            # 添加到历史
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "Min错误", f"错误: {str(e)}")

    def wrap_expression(self, func_name):
        """将表达式包装在函数中"""
        cursor_pos = self.expression_input.cursorPosition()
        selected_text = self.expression_input.selectedText()

        if selected_text:
            # 有选中文本，将其放入函数中
            new_text = f"{func_name}({selected_text})"
            self.current_expression = (
                self.current_expression[:self.expression_input.selectionStart()] +
                new_text +
                self.current_expression[self.expression_input.selectionEnd():]
            )
            new_cursor_pos = self.expression_input.selectionStart() + len(new_text)
        else:
            # 无选中文本，插入函数模板
            new_text = f"{func_name}()"
            self.current_expression = (
                self.current_expression[:cursor_pos] +
                new_text +
                self.current_expression[cursor_pos:]
            )
            new_cursor_pos = cursor_pos + len(func_name) + 1  # 光标位于括号内

        self.expression_input.setText(self.current_expression)
        self.expression_input.setCursorPosition(new_cursor_pos)
        self.update_input_latex_display()

    def insert_answer(self):
        """插入上一个答案"""
        if hasattr(self, "last_answer"):
            self.add_to_expression(str(self.last_answer))
        else:
            QMessageBox.information(self, "提示", "尚无可用的上一个答案")

    def toggle_sign(self):
        """切换正负号"""
        cursor_pos = self.expression_input.cursorPosition()
        selected_text = self.expression_input.selectedText()

        if selected_text:
            # 有选中文本，在其前添加负号
            new_text = f"-({selected_text})"
            self.current_expression = (
                self.current_expression[:self.expression_input.selectionStart()] +
                new_text +
                self.current_expression[self.expression_input.selectionEnd():]
            )
            new_cursor_pos = self.expression_input.selectionStart() + len(new_text)
        else:
            # 无选中文本，检查光标位置前是否有数字或表达式
            # 这里简化处理，直接插入"(-1)*"
            new_text = "(-1)*"
            self.current_expression = (
                self.current_expression[:cursor_pos] +
                new_text +
                self.current_expression[cursor_pos:]
            )
            new_cursor_pos = cursor_pos + len(new_text)

        self.expression_input.setText(self.current_expression)
        self.expression_input.setCursorPosition(new_cursor_pos)
        self.update_input_latex_display()

    def add_to_history(self, item):
        """添加项目到历史记录"""
        self.history.append(item)
        if hasattr(self, "history_list"):
            self.history_list.addItem(item)

    def create_display_area(self):
        """创建显示区域，包含表达式输入和LaTeX渲染（输入和结果分开）"""
        display_splitter = QSplitter(Qt.Vertical)

        # 表达式输入框
        self.expression_input = QLineEdit()
        self.expression_input.setPlaceholderText("Enter expression here...")
        self.expression_input.textChanged.connect(self.on_expression_changed)
        self.expression_input.selectionChanged.connect(self.update_input_latex_display)
        self.expression_input.returnPressed.connect(self.calculate)
        display_splitter.addWidget(self.expression_input)

        # 输入LaTeX显示
        self.input_latex_view = QWebEngineView()
        display_splitter.addWidget(self.input_latex_view)

        # 结果LaTeX显示
        self.result_latex_view = QWebEngineView()
        display_splitter.addWidget(self.result_latex_view)

        display_splitter.setSizes([50, 150, 150])
        self.main_layout.addWidget(display_splitter)

        # 初始化显示为空
        self.input_latex_view.setHtml("<html><body></body></html>")
        self.result_latex_view.setHtml("<html><body></body></html>")

    def create_tabs(self):
        """创建所有标签页"""
        self.create_basic_tab()
        self.create_algebra_tab()
        self.create_trigonometry_tab()
        self.create_calculus_tab()
        self.create_statistics_tab()
        self.create_matrix_tab()
        self.create_characters_tab()
        self.create_history_tab()
        self.create_graph_tab()

    def update_input_latex_display(self):
        """将输入内容直接以latex形式展示，并高亮选中内容"""
        text = self.expression_input.text()
        sel_start = self.expression_input.selectionStart()
        sel_len = len(self.expression_input.selectedText())

        # 处理常用的LaTeX替换，使用改进的方法
        latex_text = self.convert_to_latex_improved(text)

        if sel_len > 0:
            # 获取LaTeX形式的选中文本，使用改进的方法
            selected_latex = self.convert_to_latex_improved(text[sel_start:sel_start+sel_len])

            # 高亮选中内容
            highlighted = (
                latex_text[:sel_start] +
                "<mark>" + selected_latex + "</mark>" +
                latex_text[sel_start+sel_len:]
            )
        else:
            highlighted = latex_text

        # 如果表达式为空，不显示任何LaTeX内容
        if not text:
            self.input_latex_view.setHtml("<html><body></body></html>")
            return

        # 展示LaTeX内容
        latex_html = f"""
        <html>
        <head>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        </head>
        <body>
            <div style="font-size: 24px; text-align: center; padding: 20px;">
                $${highlighted}$$
            </div>
        </body>
        </html>
        """
        self.input_latex_view.setHtml(latex_html)

    def convert_to_latex(self, text):
        """将计算器表达式转换为LaTeX格式"""
        # 定义替换规则
        replacements = [
            ('pi', '\\pi'),
            ('*', '\\times'),
            ('/', '\\div'),
            ('sqrt(', '\\sqrt{'),
            (')', '}'),
            ('**', '^'),
            ('1/(', '\\frac{1}{'),
            ('sin(', '\\sin('),
            ('cos(', '\\cos('),
            ('tan(', '\\tan('),
            ('log(', '\\log(')
        ]

        # 应用替换规则
        latex_text = text
        for pattern, replacement in replacements:
            latex_text = latex_text.replace(pattern, replacement)

        return latex_text

    def convert_to_latex_improved(self, text):
        """将计算器表达式转换为LaTeX格式，使用标准的花括号语法"""
        # 定义替换规则 - 按优先级排序
        replacements = [
            # 特殊常量
            ('pi', '\\pi'),

            # 运算符
            ('*', '\\times'),
            ('/', '\\div'),
            ('**', '^'),

            # 函数和括号 - 使用花括号
            ('sqrt(', '\\sqrt{'),
            ('sin(', '\\sin{'),
            ('cos(', '\\cos{'),
            ('tan(', '\\tan{'),
            ('asin(', '\\arcsin{'),
            ('acos(', '\\arccos{'),
            ('atan(', '\\arctan{'),
            ('log(', '\\log{'),
            ('ln(', '\\ln{'),

            # 分数
            ('1/(', '\\frac{1}{'),

            # 最后处理所有右括号
            (')', '}')
        ]

        # 应用替换规则
        latex_text = text
        for pattern, replacement in replacements:
            latex_text = latex_text.replace(pattern, replacement)

        return latex_text

    def update_result_latex_display(self, latex_str):
        """以latex形式展示结果（sympy代码生成）"""
        # 如果结果为空，不显示任何LaTeX内容
        if not latex_str:
            self.result_latex_view.setHtml("<html><body></body></html>")
            return

        latex_html = f"""
        <html>
        <head>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        </head>
        <body>
            <div style="font-size: 24px; text-align: center; padding: 20px; color: green;">
                $${latex_str}$$
            </div>
        </body>
        </html>
        """
        self.result_latex_view.setHtml(latex_html)

    def toggle_angle_mode(self):
        """切换角度制和弧度制"""
        if self.angle_mode == "RAD":
            self.angle_mode = "DEG"
        else:
            self.angle_mode = "RAD"

        # 更新按钮文本
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "Basic":
                basic_tab = self.tab_widget.widget(i)
                for child in basic_tab.children():
                    if isinstance(child, QPushButton) and (child.text() == "DEG" or child.text() == "RAD"):
                        child.setText(self.angle_mode)
                        break
                break

        # 显示状态信息
        QMessageBox.information(self, "Mode Changed", f"Calculator now in {self.angle_mode} mode")

    def create_basic_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, "Basic")

        grid_layout = QGridLayout(tab)

        # 定义按钮及其位置
        buttons = [
            (self.angle_mode, 0, 0), ('π', 0, 1), ('%', 0, 2), ('(', 0, 3), (')', 0, 4), ('÷', 0, 5),
            ('^', 1, 0), ('e', 1, 1), ('7', 1, 2), ('8', 1, 3), ('9', 1, 4), ('×', 1, 5),
            ('√', 2, 0), ('x', 2, 1), ('4', 2, 2), ('5', 2, 3), ('6', 2, 4), ('-', 2, 5),
            ('log', 3, 0), ('y', 3, 1), ('1', 3, 2), ('2', 3, 3), ('3', 3, 4), ('+', 3, 5),
            ('1/', 4, 0), ('sin', 4, 1), ('cos', 4, 2), ('0', 4, 3), ('.', 4, 4), ('=', 4, 5)
        ]

        # 创建按钮并添加到布局
        for btn_text, row, col in buttons:
            button = QPushButton(btn_text)
            button.setMinimumHeight(40)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 让按钮填充网格
            button.clicked.connect(self.on_button_clicked)
            grid_layout.addWidget(button, row, col, 1, 1)  # rowSpan=1, colSpan=1

    def create_algebra_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, "Algebra")

        grid_layout = QGridLayout(tab)
        label = QLabel("Algebra Functions:")
        grid_layout.addWidget(label, 0, 0, 1, 2)

        algebra_buttons = [
            ("Solve Equation", self.solve_equation),
            ("Factor", lambda: self.apply_operation(sp.factor)),
            ("Expand", lambda: self.apply_operation(sp.expand)),
            ("Simplify", lambda: self.apply_operation(sp.simplify)),
            ("Polynomial Roots", self.find_roots)
        ]
        for idx, (text, handler) in enumerate(algebra_buttons):
            btn = QPushButton(text)
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(handler)
            grid_layout.addWidget(btn, 1 + idx // 2, idx % 2, 1, 1)

    def create_trigonometry_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, "Trigonometry")

        grid_layout = QGridLayout(tab)
        label = QLabel("Trigonometry Functions:")
        grid_layout.addWidget(label, 0, 0, 1, 3)

        trig_buttons = [
            ("sin(x)", lambda: self.add_function("sin({})")),
            ("cos(x)", lambda: self.add_function("cos({})")),
            ("tan(x)", lambda: self.add_function("tan({})")),
            ("asin(x)", lambda: self.add_function("asin({})")),
            ("acos(x)", lambda: self.add_function("acos({})")),
            ("atan(x)", lambda: self.add_function("atan({})")),
            ("sinh(x)", lambda: self.add_function("sinh({})")),
            ("cosh(x)", lambda: self.add_function("cosh({})")),
            ("tanh(x)", lambda: self.add_function("tanh({})"))
        ]
        for idx, (text, handler) in enumerate(trig_buttons):
            btn = QPushButton(text)
            btn.setMinimumHeight(35)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(handler)
            grid_layout.addWidget(btn, 1 + idx // 3, idx % 3, 1, 1)

    def create_calculus_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, "Calculus")

        grid_layout = QGridLayout(tab)
        label = QLabel("Calculus Functions:")
        grid_layout.addWidget(label, 0, 0, 1, 2)

        calculus_buttons = [
            ("Derivative", self.calculate_derivative),
            ("Integral", self.calculate_integral),
            ("Limit", self.calculate_limit),
            ("Taylor Series", self.calculate_taylor_series)
        ]
        for idx, (text, handler) in enumerate(calculus_buttons):
            btn = QPushButton(text)
            btn.setMinimumHeight(35)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(handler)
            grid_layout.addWidget(btn, 1 + idx // 2, idx % 2, 1, 1)

    def create_statistics_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, "Statistics")

        grid_layout = QGridLayout(tab)
        label = QLabel("Statistical Functions:")
        grid_layout.addWidget(label, 0, 0, 1, 2)

        stats_buttons = [
            ("Mean", self.calculate_mean),
            ("Median", self.calculate_median),
            ("Mode", self.calculate_mode),
            ("Standard Deviation", self.calculate_std),
            ("Variance", self.calculate_variance)
        ]
        for idx, (text, handler) in enumerate(stats_buttons):
            btn = QPushButton(text)
            btn.setMinimumHeight(35)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(handler)
            grid_layout.addWidget(btn, 1 + idx // 2, idx % 2, 1, 1)

        self.stats_input = QLineEdit()
        self.stats_input.setPlaceholderText("Enter comma-separated numbers")
        grid_layout.addWidget(self.stats_input, 4, 0, 1, 2)

    def create_matrix_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, "Matrix")

        grid_layout = QGridLayout(tab)
        label = QLabel("Matrix Operations:")
        grid_layout.addWidget(label, 0, 0, 1, 2)

        self.matrix_input = QLineEdit()
        self.matrix_input.setPlaceholderText("Enter matrix: [[1,2],[3,4]]")
        grid_layout.addWidget(self.matrix_input, 1, 0, 1, 2)

        matrix_buttons = [
            ("Matrix Addition", self.matrix_addition),
            ("Matrix Multiplication", self.matrix_multiplication),
            ("Determinant", self.matrix_determinant),
            ("Inverse", self.matrix_inverse),
            ("Transpose", self.matrix_transpose)
        ]
        for idx, (text, handler) in enumerate(matrix_buttons):
            btn = QPushButton(text)
            btn.setMinimumHeight(35)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(handler)
            grid_layout.addWidget(btn, 2 + idx // 2, idx % 2, 1, 1)

    def create_characters_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, "Characters")

        grid_layout = QGridLayout(tab)
        label = QLabel("Special Characters:")
        grid_layout.addWidget(label, 0, 0, 1, 8)

        chars = "αβγδεζηθικλμνξοπρστυφχψωΔΘΛΞΠΣΦΨΩ∫∑∏√∞≈≠≤≥"
        for idx, char in enumerate(chars):
            btn = QPushButton(char)
            btn.setFixedSize(40, 40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(lambda _, c=char: self.add_to_expression(c))
            grid_layout.addWidget(btn, 1 + idx // 8, idx % 8, 1, 1)

    def create_history_tab(self):
        tab = QWidget()
        self.tab_widget.addTab(tab, "History")
        tab.setObjectName("History")

        layout = QVBoxLayout(tab)
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.on_history_item_clicked)
        layout.addWidget(self.history_list)

        # 添加清除历史按钮
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)

    def create_graph_tab(self):
        """创建绘图标签页"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "Graph")
        tab.setObjectName("Graph")

        layout = QVBoxLayout(tab)

        # 函数输入框
        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("Enter function of x, e.g., sin(x), x^2")
        layout.addWidget(self.function_input)

        # 绘图按钮
        plot_btn = QPushButton("Plot Function")
        plot_btn.clicked.connect(self.plot_function)
        layout.addWidget(plot_btn)

        # 范围设置
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("x min:"))
        self.xmin_input = QLineEdit("-10")
        range_layout.addWidget(self.xmin_input)

        range_layout.addWidget(QLabel("x max:"))
        self.xmax_input = QLineEdit("10")
        range_layout.addWidget(self.xmax_input)

        range_layout.addWidget(QLabel("y min:"))
        self.ymin_input = QLineEdit("-10")
        range_layout.addWidget(self.ymin_input)

        range_layout.addWidget(QLabel("y max:"))
        self.ymax_input = QLineEdit("10")
        range_layout.addWidget(self.ymax_input)

        layout.addLayout(range_layout)

        # 显示绘图区域
        self.graph_canvas = FigureCanvas(Figure(figsize=(5, 4), dpi=100))
        layout.addWidget(self.graph_canvas)

    def create_control_buttons(self):
        control_layout = QHBoxLayout()
        self.main_layout.addLayout(control_layout)

        # 控制按钮
        controls = [
            ("CLR", self.clear_display),
            ("←", self.move_cursor_left),
            ("→", self.move_cursor_right),
            ("⌫", self.backspace),
            ("Calc", self.calculate)
        ]

        for text, handler in controls:
            btn = QPushButton(text)
            btn.setMinimumHeight(40)
            btn.clicked.connect(handler)
            control_layout.addWidget(btn)

    def create_menus(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New", self.new_calculation).setShortcut("Ctrl+N")
        file_menu.addSeparator()
        file_menu.addAction("Import", self.import_data).setShortcut("Ctrl+I")
        file_menu.addAction("Export", self.export_data).setShortcut("Ctrl+E")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close).setShortcut("Ctrl+Q")

        # 视图菜单
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Show Graph", self.show_graph_tab)
        view_menu.addAction("Show History", self.show_history_tab)

        # 帮助菜单
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Documentation", self.show_documentation)
        help_menu.addAction("About", self.show_about)

    def on_tab_changed(self, index):
        """标签页切换事件处理"""
        # 这里可以根据需要添加标签页切换逻辑
        pass

    def clear_display(self):
        self.current_expression = ""
        self.expression_input.clear()
        self.update_input_latex_display()
        self.update_result_latex_display("")

    def add_to_expression(self, text, latex_text=None):
        """向表达式添加文本，可选择指定不同的LaTeX表示"""
        # 如果没有提供LaTeX文本，则使用原始文本
        if latex_text is None:
            latex_text = text

        cursor_pos = self.expression_input.cursorPosition()
        self.current_expression = (
            self.current_expression[:cursor_pos] +
            text +
            self.current_expression[cursor_pos:]
        )
        self.expression_input.setText(self.current_expression)
        self.expression_input.setCursorPosition(cursor_pos + len(text))
        self.update_input_latex_display()

    def add_to_expression_with_cursor(self, text, latex_open, latex_close):
        """添加需要光标定位的表达式（如函数、分数等）"""
        cursor_pos = self.expression_input.cursorPosition()
        selected_text = self.expression_input.selectedText()

        # 代码文本处理
        if selected_text:
            # 如果有选中文本，将其放入函数/表达式中
            if text.endswith('('):
                # 函数类型
                code_text = f"{text}{selected_text})"
            else:
                # 其他类型（如分数）
                code_text = f"{text}{selected_text})"
        else:
            # 无选中文本，插入占位符
            if text.endswith('('):
                # 函数类型
                code_text = f"{text})"
                cursor_offset = -1  # 光标位于右括号前
            else:
                # 其他类型（如分数）
                code_text = f"{text})"
                cursor_offset = -1  # 光标位于右括号前

        # 更新表达式
        self.current_expression = (
            self.current_expression[:cursor_pos] +
            code_text +
            self.current_expression[cursor_pos:]
        )
        self.expression_input.setText(self.current_expression)

        # 设置光标位置
        if selected_text:
            # 如果有选中文本，光标位于插入内容之后
            self.expression_input.setCursorPosition(cursor_pos + len(code_text))
        else:
            # 如果没有选中文本，光标位于插入内容中的适当位置
            self.expression_input.setCursorPosition(cursor_pos + len(code_text) + cursor_offset)

        self.update_input_latex_display()

    def add_function(self, template):
        cursor_pos = self.expression_input.cursorPosition()
        selected_text = self.expression_input.selectedText()
        if selected_text:
            new_text = template.format(selected_text)
            self.current_expression = (
                self.current_expression[:self.expression_input.selectionStart()] +
                new_text +
                self.current_expression[self.expression_input.selectionEnd():]
            )
            new_cursor_pos = self.expression_input.selectionStart() + len(new_text)
        else:
            new_text = template.format("")
            self.current_expression = (
                self.current_expression[:cursor_pos] +
                new_text +
                self.current_expression[cursor_pos:]
            )
            new_cursor_pos = cursor_pos + len(new_text) - 1
        self.expression_input.setText(self.current_expression)
        self.expression_input.setCursorPosition(new_cursor_pos)
        self.update_input_latex_display()

    def backspace(self):
        cursor_pos = self.expression_input.cursorPosition()
        if cursor_pos > 0:
            self.current_expression = (
                self.current_expression[:cursor_pos - 1] +
                self.current_expression[cursor_pos:]
            )
            self.expression_input.setText(self.current_expression)
            self.expression_input.setCursorPosition(cursor_pos - 1)
            self.update_input_latex_display()

    def on_button_clicked(self):
        button = self.sender()
        text = button.text()

        # 特殊按钮处理
        special_buttons = {
            '⌫': self.backspace,
            'CLR': self.clear_display,
            '←': self.move_cursor_left,
            '→': self.move_cursor_right
        }

        if text == '=':
            # 等号键有两种功能：计算结果或添加等号字符
            if self.expression_input.text().strip().endswith('='):
                # 如果表达式已经以等号结尾，则计算结果
                self.calculate()
            else:
                # 否则添加等号字符
                self.add_to_expression('=', '=')
        elif text == 'DEG' or text == 'RAD':
            # 角度制/弧度制切换
            self.toggle_angle_mode()
        elif text in special_buttons:
            special_buttons[text]()
        else:
            # 处理特殊符号和LaTeX展示
            latex_replacements = {
                'π': ['\\pi'],
                '÷': ['/'],
                '×': ['\\times'],
                '√': ['\\sqrt{', '}'],
                '^': ['^{', '}'],
                '1/': ['\\frac{1}{', '}'],
                'sin': ['\\sin(', ')'],
                'cos': ['\\cos(', ')'],
                'tan': ['\\tan(', ')'],
                'log': ['\\log(', ')'],
                'e': ['e']
            }

            code_replacements = {
                'π': 'pi',
                '÷': '/',
                '×': '*',
                '√': 'sqrt(',
                '^': '**',
                '1/': '1/('
            }

            # 检查是否为特殊LaTeX符号
            if text in latex_replacements:
                latex_parts = latex_replacements[text]
                if len(latex_parts) == 1:
                    # 单个符号
                    self.add_to_expression(code_replacements.get(text, text), latex_parts[0])
                elif len(latex_parts) == 2:
                    # 函数或有开始/结束的符号
                    self.add_to_expression_with_cursor(code_replacements.get(text, text), latex_parts[0], latex_parts[1])
            else:
                # 普通符号或数字
                self.add_to_expression(text, text)

    def on_expression_changed(self, text):
        """输入框内容变化时，更新输入latex展示"""
        self.current_expression = text
        # 使用带光标的更新方法
        self.update_input_latex_display_with_cursor()

    def move_cursor_left(self):
        cursor_pos = self.expression_input.cursorPosition()
        if cursor_pos > 0:
            self.expression_input.setCursorPosition(cursor_pos - 1)
            # 更新显示以突出显示光标位置
            self.update_input_latex_display_with_cursor()

    def move_cursor_right(self):
        cursor_pos = self.expression_input.cursorPosition()
        if cursor_pos < len(self.current_expression):
            self.expression_input.setCursorPosition(cursor_pos + 1)
            # 更新显示以突出显示光标位置
            self.update_input_latex_display_with_cursor()

    def update_input_latex_display_with_cursor(self):
        """更新输入显示并显示光标位置"""
        try:
            text = self.expression_input.text()
            cursor_pos = self.expression_input.cursorPosition()

            if not text:
                self.input_latex_view.setHtml("<html><body></body></html>")
                return

            # 转换为LaTeX格式
            latex_text = self.convert_to_latex_improved(text)

            # 在光标位置插入一个竖线符号
            if cursor_pos < len(text):
                cursor_char = text[cursor_pos]
                latex_cursor_char = self.convert_to_latex_improved(cursor_char)
                latex_text_with_cursor = (
                    self.convert_to_latex_improved(text[:cursor_pos]) +
                    "\\color{red}|" +  # 插入红色竖线作为光标
                    self.convert_to_latex_improved(text[cursor_pos:])
                )
            else:
                # 光标在文本末尾
                latex_text_with_cursor = latex_text + "\\color{red}|"
        except Exception as e:
            # 如果发生任何错误，显示友好的错误提示
            print(f"LaTeX rendering error: {str(e)}")
            error_html = """
            <html>
            <body>
                <div style="font-size: 16px; text-align: center; padding: 20px; color: #666;">
                    数学表达式显示正在处理中...
                </div>
            </body>
            </html>
            """
            self.input_latex_view.setHtml(error_html)
            return

        try:
            # 展示LaTeX内容
            latex_html = f"""
            <html>
            <head>
                <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
                <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            </head>
            <body>
                <div style="font-size: 24px; text-align: center; padding: 20px;">
                    $${latex_text_with_cursor}$$
                </div>
            </body>
            </html>
            """
            self.input_latex_view.setHtml(latex_html)
        except Exception as e:
            # 如果展示LaTeX出错，显示友好的错误提示
            print(f"LaTeX display error: {str(e)}")
            error_html = """
            <html>
            <body>
                <div style="font-size: 16px; text-align: center; padding: 20px; color: #666;">
                    数学表达式显示正在处理中...
                </div>
            </body>
            </html>
            """
            self.input_latex_view.setHtml(error_html)

    def convert_trig_to_radians(self, expression):
        """在角度制模式下将三角函数的参数从角度转换为弧度"""
        import re

        # 定义要处理的三角函数列表
        trig_functions = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']

        # 替换每个三角函数调用
        modified_expr = expression
        for func in trig_functions:
            # 匹配函数调用，例如sin(45)
            pattern = fr'{func}\(([^()]+)\)'

            # 替换为转换后的表达式
            if func in ['sin', 'cos', 'tan']:
                # 将角度转换为弧度: sin(45) -> sin(45*pi/180)
                modified_expr = re.sub(pattern, fr'{func}(()*pi/180)', modified_expr)
            else:
                # 反三角函数需要相反的转换: asin(0.5) -> asin(0.5)*180/pi
                # 这里不改变参数，而是将结果转换为角度
                modified_expr = re.sub(pattern, fr'{func}()*180/pi', modified_expr)

        return modified_expr

    def calculate(self):
        """用sympy解析并计算，结果以latex形式展示"""
        try:
            if not self.current_expression:
                return

            # 检查表达式是否包含等号，如果有，移除它
            expression_to_calculate = self.current_expression
            if expression_to_calculate.endswith('='):
                expression_to_calculate = expression_to_calculate[:-1]

            # 在角度制模式下处理三角函数
            if self.angle_mode == "DEG":
                # 替换三角函数调用，添加角度转弧度的转换
                if 'sin(' in expression_to_calculate:
                    expression_to_calculate = expression_to_calculate.replace('sin(', 'sin(pi/180*')
                if 'cos(' in expression_to_calculate:
                    expression_to_calculate = expression_to_calculate.replace('cos(', 'cos(pi/180*')
                if 'tan(' in expression_to_calculate:
                    expression_to_calculate = expression_to_calculate.replace('tan(', 'tan(pi/180*')
                # 反三角函数结果需要从弧度转为角度
                if 'asin(' in expression_to_calculate:
                    expression_to_calculate = expression_to_calculate.replace('asin(', '(180/pi)*asin(')
                if 'acos(' in expression_to_calculate:
                    expression_to_calculate = expression_to_calculate.replace('acos(', '(180/pi)*acos(')
                if 'atan(' in expression_to_calculate:
                    expression_to_calculate = expression_to_calculate.replace('atan(', '(180/pi)*atan(')

            expr = parse_expr(expression_to_calculate.replace('×', '*').replace('÷', '/'),
                              local_dict={'x': self.x, 'y': self.y},
                              transformations=self.transformations)
            result = expr
            latex_result = sp.latex(result)
            self.update_result_latex_display(latex_result)

            # 添加到历史
            history_item = f"{self.current_expression} = {result}"
            self.history.append(history_item)
            self.history_list.addItem(history_item)
        except Exception as e:
            self.update_result_latex_display(f"\\text{{Error: {str(e)}}}")

    def apply_operation(self, operation):
        """应用SymPy操作"""
        try:
            if not self.current_expression:
                return

            expr = parse_expr(self.current_expression,
                              local_dict={'x': self.x, 'y': self.y},
                              transformations=self.transformations)
            result = operation(expr)
            self.current_expression = str(result)
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Operation Error", f"Error: {str(e)}")

    def solve_equation(self):
        """解方程"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "Input Error", "Please enter an equation first")
                return

            expr = parse_expr(self.current_expression,
                              local_dict={'x': self.x, 'y': self.y},
                              transformations=self.transformations)
            solutions = sp.solve(expr, self.x)

            if solutions:
                if len(solutions) == 1:
                    self.current_expression = f"x = {solutions[0]}"
                else:
                    self.current_expression = "Solutions: " + ", ".join([f"x = {s}" for s in solutions])
            else:
                self.current_expression = "No solution found"

            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Solve Error", f"Error: {str(e)}")

    def find_roots(self):
        """求多项式根"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "Input Error", "Please enter a polynomial first")
                return

            expr = parse_expr(self.current_expression,
                              local_dict={'x': self.x, 'y': self.y},
                              transformations=self.transformations)
            roots = sp.roots(expr, self.x)

            if roots:
                root_str = ", ".join([f"{k} (multiplicity {v})" for k, v in roots.items()])
                self.current_expression = f"Roots: {root_str}"
            else:
                self.current_expression = "No roots found or not a polynomial"

            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Roots Error", f"Error: {str(e)}")

    def calculate_derivative(self):
        """计算导数"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "Input Error", "Please enter an expression first")
                return

            expr = parse_expr(self.current_expression,
                              local_dict={'x': self.x, 'y': self.y},
                              transformations=self.transformations)
            derivative = sp.diff(expr, self.x)
            self.current_expression = f"d/dx {self.current_expression} = {derivative}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Derivative Error", f"Error: {str(e)}")

    def calculate_integral(self):
        """计算积分"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "Input Error", "Please enter an expression first")
                return

            expr = parse_expr(self.current_expression,
                              local_dict={'x': self.x, 'y': self.y},
                              transformations=self.transformations)
            integral = sp.integrate(expr, self.x)
            self.current_expression = f"∫{self.current_expression}dx = {integral} + C"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Integral Error", f"Error: {str(e)}")

    def calculate_limit(self):
        """计算极限"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "Input Error", "Please enter an expression first")
                return

            # 假设用户输入格式为 "表达式, x->a"
            if "," in self.current_expression:
                expr_str, limit_str = self.current_expression.split(",", 1)
                expr = parse_expr(expr_str,
                                  local_dict={'x': self.x, 'y': self.y},
                                  transformations=self.transformations)

                # 解析极限表达式
                if "->" in limit_str:
                    var, point = limit_str.split("->", 1)
                    var = var.strip()
                    point = point.strip()

                    limit = sp.limit(expr, sp.Symbol(var), parse_expr(point))
                    self.current_expression = f"lim_{{{var}->{point}}} {expr_str} = {limit}"
                else:
                    self.current_expression = "Invalid limit format. Use: expr, x->a"
            else:
                self.current_expression = "Enter expression and limit, e.g., sin(x)/x, x->0"

            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Limit Error", f"Error: {str(e)}")

    def calculate_taylor_series(self):
        """计算泰勒级数"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "Input Error", "Please enter an expression first")
                return

            # 假设用户输入格式为 "表达式, x, a, n"
            parts = self.current_expression.split(",")
            if len(parts) >= 3:
                expr = parse_expr(parts[0].strip(),
                                  local_dict={'x': self.x, 'y': self.y},
                                  transformations=self.transformations)
                var = sp.Symbol(parts[1].strip())
                a = parse_expr(parts[2].strip())
                n = 4 if len(parts) < 4 else int(parts[3].strip())

                series = sp.series(expr, var, a, n).removeO()
                self.current_expression = f"Taylor series of {parts[0].strip()} around {var}={a} (order {n}): {series}"
            else:
                self.current_expression = "Enter: expr, x, a, [n] (n defaults to 4)"

            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Taylor Series Error", f"Error: {str(e)}")

    def plot_function(self):
        """绘制函数图像"""
        try:
            func_str = self.function_input.text()
            if not func_str:
                QMessageBox.warning(self, "Input Error", "Please enter a function first")
                return

            # 验证并解析x范围
            try:
                x_min = float(self.xmin_input.text())
                x_max = float(self.xmax_input.text())
                y_min = float(self.ymin_input.text())
                y_max = float(self.ymax_input.text())
            except ValueError:
                raise ValueError("Range values must be numbers")

            if x_min >= x_max:
                raise ValueError("x min must be less than x max")

            if y_min >= y_max:
                raise ValueError("y min must be less than y max")

            # 使用SymPy解析函数
            expr = parse_expr(func_str,
                              local_dict={'x': self.x},
                              transformations=self.transformations)

            # 转换为可计算的lambda函数
            f = sp.lambdify(self.x, expr, modules=['numpy'])

            # 生成x值
            x_vals = np.linspace(x_min, x_max, 400)
            y_vals = f(x_vals)

            # 清除图形并绘制新图
            fig = self.graph_canvas.figure
            fig.clear()

            ax = fig.add_subplot(111)
            ax.plot(x_vals, y_vals)
            ax.grid(True)
            ax.set_xlabel('x')
            ax.set_ylabel('f(x)')
            ax.set_title(f'Plot of {func_str}')
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)

            fig.tight_layout()
            self.graph_canvas.draw()

        except Exception as e:
            fig = self.graph_canvas.figure
            fig.clear()
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error: {str(e)}", ha='center', va='center', transform=ax.transAxes)
            fig.tight_layout()
            self.graph_canvas.draw()
            QMessageBox.critical(self, "Plot Error", f"Error: {str(e)}")

    def show_graph_tab(self):
        """显示绘图标签页"""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i).objectName() == "Graph":
                self.tab_widget.setCurrentIndex(i)
                break

    def show_history_tab(self):
        """显示历史标签页"""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i).objectName() == "History":
                self.tab_widget.setCurrentIndex(i)
                break

    def on_history_item_clicked(self, item):
        """历史记录项被双击时，将表达式加载到输入框"""
        text = item.text()
        # 提取等号前的表达式
        if '=' in text:
            expr = text.split('=', 1)[0].strip()
            self.current_expression = expr
            self.expression_input.setText(expr)
            self.update_input_latex_display()
            self.update_result_latex_display("")
            # 切换到基本标签页
            self.tab_widget.setCurrentIndex(0)

    def clear_history(self):
        """清除历史记录"""
        self.history.clear()
        self.history_list.clear()

    def new_calculation(self):
        """新建计算"""
        self.clear_display()
        self.tab_widget.setCurrentIndex(0)

    def import_data(self):
        """导入数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Data", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    self.current_expression = content
                    self.expression_input.setText(content)
                    self.update_input_latex_display()
                    self.update_result_latex_display("")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Error importing file: {str(e)}")

    def export_data(self):
        """导出数据"""
        if not self.current_expression:
            QMessageBox.warning(self, "Export Error", "Nothing to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.current_expression)
                QMessageBox.information(self, "Export Success", "Data exported successfully")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Error exporting file: {str(e)}")

    def show_about(self):
        """显示关于信息"""
        about_text = """
        <h2>Kalculate</h2>
        <p>A scientific calculator with SymPy backend</p>
        <p>Version 1.0</p>
        <p>Features:</p>
        <ul>
            <li>Symbolic computation with SymPy</li>
            <li>LaTeX rendering of expressions</li>
            <li>Function plotting with Matplotlib</li>
            <li>Algebra, Calculus, Statistics and more</li>
        </ul>
        """

        msg = QMessageBox()
        msg.setWindowTitle("About Kalculate")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.exec()

    def show_documentation(self):
        """显示帮助文档"""
        QMessageBox.information(
            self, "Documentation",
            "Kalculate User Guide:\n\n"
            "1. Basic Calculations: Use the Basic tab for arithmetic operations\n"
            "2. Algebra: Solve equations, factor, expand expressions\n"
            "3. Calculus: Compute derivatives, integrals, limits, and Taylor series\n"
            "4. Graphing: Enter a function of x in the Graph tab to plot it"
            "5. History: Double-click any history item to reuse it"
            "6. Use the input box at the top to edit expressions directly"
        )

    def calculate_mean(self):
        """计算平均值"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "Input Error", "Please enter data first")
                return

            # 解析输入数据
            data = [float(x) for x in data_str.split(",")]
            mean_value = np.mean(data)

            # 显示结果
            self.current_expression = f"Mean: {mean_value}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Mean Error", f"Error: {str(e)}")

    def calculate_median(self):
        """计算中位数"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "Input Error", "Please enter data first")
                return

            # 解析输入数据
            data = [float(x) for x in data_str.split(",")]
            median_value = np.median(data)

            # 显示结果
            self.current_expression = f"Median: {median_value}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Median Error", f"Error: {str(e)}")

    def calculate_mode(self):
        """计算众数"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "Input Error", "Please enter data first")
                return

            # 解析输入数据
            data = [float(x) for x in data_str.split(",")]

            # 使用NumPy计算众数
            unique_values, counts = np.unique(data, return_counts=True)
            mode_indices = np.argwhere(counts == np.max(counts)).flatten()
            mode_values = unique_values[mode_indices]

            # 显示结果
            if len(mode_values) == 1:
                mode_text = f"{mode_values[0]}"
            else:
                mode_text = f"{list(mode_values)}"

            self.current_expression = f"Mode: {mode_text}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Mode Error", f"Error: {str(e)}")

    def calculate_std(self):
        """计算标准差"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "Input Error", "Please enter data first")
                return

            # 解析输入数据
            data = [float(x) for x in data_str.split(",")]
            std_value = np.std(data)

            # 显示结果
            self.current_expression = f"Standard Deviation: {std_value}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Standard Deviation Error", f"Error: {str(e)}")

    def calculate_variance(self):
        """计算方差"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "Input Error", "Please enter data first")
                return

            # 解析输入数据
            data = [float(x) for x in data_str.split(",")]
            variance_value = np.var(data)

            # 显示结果
            self.current_expression = f"Variance: {variance_value}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Variance Error", f"Error: {str(e)}")

    def matrix_addition(self):
        """矩阵加法"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "Input Error", "Please enter matrices")
                return

            # 解析输入的矩阵
            matrices = self.current_expression.split(";")
            if len(matrices) != 2:
                QMessageBox.warning(self, "Input Error", "Enter two matrices separated by ';'")
                return

            mat1 = np.array(eval(matrices[0]))
            mat2 = np.array(eval(matrices[1]))
            result = mat1 + mat2

            # 显示结果
            self.current_expression = f"{mat1} + {mat2} = {result}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Matrix Addition Error", f"Error: {str(e)}")

    def matrix_multiplication(self):
        """矩阵乘法"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "Input Error", "Please enter matrices")
                return

            # 解析输入的矩阵
            matrices = self.current_expression.split(";")
            if len(matrices) != 2:
                QMessageBox.warning(self, "Input Error", "Enter two matrices separated by ';'")
                return

            mat1 = np.array(eval(matrices[0]))
            mat2 = np.array(eval(matrices[1]))
            result = mat1 @ mat2  # 矩阵乘法

            # 显示结果
            self.current_expression = f"{mat1} * {mat2} = {result}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Matrix Multiplication Error", f"Error: {str(e)}")

    def matrix_determinant(self):
        """计算矩阵行列式"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "Input Error", "Please enter a matrix")
                return

            # 解析输入的矩阵
            matrix = np.array(eval(self.current_expression))
            det = np.linalg.det(matrix)

            # 显示结果
            self.current_expression = f"det({matrix}) = {det}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Determinant Error", f"Error: {str(e)}")

    def matrix_inverse(self):
        """计算矩阵逆"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "Input Error", "Please enter a matrix")
                return

            # 解析输入的矩阵
            matrix = np.array(eval(self.current_expression))
            inv = np.linalg.inv(matrix)

            # 显示结果
            self.current_expression = f"inv({matrix}) = {inv}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Inverse Error", f"Error: {str(e)}")

    def matrix_transpose(self):
        """计算矩阵转置"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "Input Error", "Please enter a matrix")
                return

            # 解析输入的矩阵
            matrix = np.array(eval(self.current_expression))
            trans = matrix.T

            # 显示结果
            self.current_expression = f"trans({matrix}) = {trans}"
            self.expression_input.setText(self.current_expression)
            self.update_input_latex_display()
            self.update_result_latex_display("")
        except Exception as e:
            QMessageBox.critical(self, "Transpose Error", f"Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    calculator = CalculatorApp()
    sys.exit(app.exec())
