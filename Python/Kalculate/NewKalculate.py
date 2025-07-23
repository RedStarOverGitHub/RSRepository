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
        self.setWindowTitle("Kalculate")

        # 加载UI文件
        loader = QUiLoader()
        self.ui = loader.load("qtUI.ui", self)
        self.setCentralWidget(self.ui)

        # 初始化符号变量
        self.x, self.y = sp.symbols('x y')
        self.current_expression = ""
        self.history = []
        self.transformations = standard_transformations + (implicit_multiplication_application,)

        # 角度制设置，默认为弧度制
        self.angle_mode = "RAD"  # 可选值："DEG"(角度制) 或 "RAD"(弧度制)

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

        # 初始化界面元素
        self.setup_ui()

        # 连接信号
        self.connect_signals()

    def setup_ui(self):
        """设置UI元素"""
        # 输入框
        self.expression_input = self.ui.lineEdit
        self.expression_input.setPlaceholderText("输入表达式...")

        # LaTeX显示视图
        self.web_view = self.ui.webEngineView
        self.web_view.setHtml("<html><body></body></html>")

        # 连接按钮信号
        self.connect_tab_buttons()

        # 统计页面输入框
        self.stats_input = self.ui.lineEdit_num

        # 连接标签页切换信号
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)

    def connect_tab_buttons(self):
        """连接所有标签页中的按钮"""
        # 基本标签页
        self.connect_buttons_in_tab(self.ui.basic_tab)

        # 代数标签页
        self.connect_buttons_in_tab(self.ui.tab_alge)

        # 三角函数标签页
        self.connect_buttons_in_tab(self.ui.trigo_tab)

        # 微积分标签页
        self.connect_buttons_in_tab(self.ui.calcu_tab)

        # 统计标签页
        self.connect_buttons_in_tab(self.ui.tab_stat)

        # 矩阵/集合标签页
        self.connect_buttons_in_tab(self.ui.tab_marset)

        # 字符标签页
        self.connect_buttons_in_tab(self.ui.tab_char)

    def connect_buttons_in_tab(self, tab):
        """连接给定标签页中的所有按钮"""
        for child in tab.findChildren(QPushButton):
            # 2nd按钮特殊处理
            if "2nd" in child.objectName():
                child.clicked.connect(lambda checked, btn=child: self.toggle_second_mode(btn))
            else:
                child.clicked.connect(lambda checked, btn=child: self.on_button_clicked(btn))

    def connect_signals(self):
        """连接信号和槽"""
        # 输入框信号
        self.expression_input.textChanged.connect(self.on_expression_changed)
        self.expression_input.returnPressed.connect(self.calculate)

    def toggle_second_mode(self, button):
        """切换2nd模式"""
        # 获取当前标签页名称
        current_tab = self.ui.tabWidget.currentWidget().objectName()

        # 切换状态
        self.second_mode[current_tab] = not self.second_mode[current_tab]

        # 更新按钮显示
        self.update_buttons_for_second_mode(current_tab)

    def update_buttons_for_second_mode(self, tab_name):
        """根据2nd模式状态更新按钮显示和功能"""
        # 获取当前标签页
        tab = getattr(self.ui, tab_name)

        # 根据不同标签页执行不同的更新逻辑
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
        # 2nd模式下更改功能
        is_second = self.second_mode["basic_tab"]

        # 示例：在2nd模式下将log变为ln
        if hasattr(self.ui, "pushButton_log"):
            if is_second:
                self.ui.pushButton_log.setText("ln")
            else:
                self.ui.pushButton_log.setText("log")

        # 示例：在2nd模式下将sqrt变为x^2
        if hasattr(self.ui, "pushButton_root"):
            if is_second:
                self.ui.pushButton_root.setText("x²")
            else:
                self.ui.pushButton_root.setText("√")

    def update_algebra_tab_buttons(self):
        """更新代数标签页按钮"""
        is_second = self.second_mode["tab_alge"]

        # 在2nd模式下更改代数功能
        if hasattr(self.ui, "pushButton_2nda"):
            # 2nd按钮高亮
            if is_second:
                self.ui.pushButton_2nda.setStyleSheet("background-color: lightblue;")
            else:
                self.ui.pushButton_2nda.setStyleSheet("")

    def update_trig_tab_buttons(self):
        """更新三角函数标签页按钮"""
        # 当2nd模式开启时，将sin、cos、tan变为asin、acos、atan
        is_second = self.second_mode["trigo_tab"]

        # 高亮2nd按钮
        if hasattr(self.ui, "pushButton_2ndt"):
            if is_second:
                self.ui.pushButton_2ndt.setStyleSheet("background-color: lightblue;")
            else:
                self.ui.pushButton_2ndt.setStyleSheet("")

        # 更改三角函数
        if hasattr(self.ui, "pushButton_sin"):
            if is_second:
                self.ui.pushButton_sin.setText("asin")
            else:
                self.ui.pushButton_sin.setText("sin")

        if hasattr(self.ui, "pushButton_cos"):
            if is_second:
                self.ui.pushButton_cos.setText("acos")
            else:
                self.ui.pushButton_cos.setText("cos")

        if hasattr(self.ui, "pushButton_tan"):
            if is_second:
                self.ui.pushButton_tan.setText("atan")
            else:
                self.ui.pushButton_tan.setText("tan")

        # 余切、正割、余割
        if hasattr(self.ui, "pushButton_cot"):
            if is_second:
                self.ui.pushButton_cot.setText("acot")
            else:
                self.ui.pushButton_cot.setText("cot")

        if hasattr(self.ui, "pushButton_sec"):
            if is_second:
                self.ui.pushButton_sec.setText("asec")
            else:
                self.ui.pushButton_sec.setText("sec")

        if hasattr(self.ui, "pushButton_csc"):
            if is_second:
                self.ui.pushButton_csc.setText("acsc")
            else:
                self.ui.pushButton_csc.setText("csc")

    def update_calculus_tab_buttons(self):
        """更新微积分标签页按钮"""
        is_second = self.second_mode["calcu_tab"]

        # 高亮2nd按钮
        if hasattr(self.ui, "pushButton_2ndc"):
            if is_second:
                self.ui.pushButton_2ndc.setStyleSheet("background-color: lightblue;")
            else:
                self.ui.pushButton_2ndc.setStyleSheet("")

        # 在2nd模式下更改微积分功能
        if hasattr(self.ui, "pushButton_diff"):
            if is_second:
                self.ui.pushButton_diff.setText("∂")
            else:
                self.ui.pushButton_diff.setText("'")

        if hasattr(self.ui, "pushButton_inter"):
            if is_second:
                self.ui.pushButton_inter.setText("∬")
            else:
                self.ui.pushButton_inter.setText("∫")

    def update_stats_tab_buttons(self):
        """更新统计标签页按钮"""
        is_second = self.second_mode["tab_stat"]

        # 高亮2nd按钮
        if hasattr(self.ui, "pushButton_2nds"):
            if is_second:
                self.ui.pushButton_2nds.setStyleSheet("background-color: lightblue;")
            else:
                self.ui.pushButton_2nds.setStyleSheet("")

    def update_matrix_tab_buttons(self):
        """更新矩阵标签页按钮"""
        is_second = self.second_mode["tab_marset"]

        # 高亮2nd按钮
        if hasattr(self.ui, "pushButton_2ndms"):
            if is_second:
                self.ui.pushButton_2ndms.setStyleSheet("background-color: lightblue;")
            else:
                self.ui.pushButton_2ndms.setStyleSheet("")

    def update_character_tab_buttons(self):
        """更新字符标签页按钮"""
        # 在2nd模式下，将小写字母变为大写字母，并显示更多特殊字符
        is_second = self.second_mode["tab_char"]

        # 高亮2nd按钮
        if hasattr(self.ui, "pushButton_2ndch"):
            if is_second:
                self.ui.pushButton_2ndch.setStyleSheet("background-color: lightblue;")
            else:
                self.ui.pushButton_2ndch.setStyleSheet("")

        # 更新字母按钮 - 小写变大写
        for letter in "abcdefghijklmnopqrstuvwxyz":
            button_name = f"pushButton_{letter}"
            if hasattr(self.ui, button_name):
                button = getattr(self.ui, button_name)
                if is_second:
                    button.setText(letter.upper())  # 转为大写
                else:
                    button.setText(letter)  # 保持小写

        # 更新希腊字母按钮 - 小写变大写
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
            button_name = f"pushButton_{name}"
            if hasattr(self.ui, button_name):
                button = getattr(self.ui, button_name)
                if is_second:
                    button.setText(upper)  # 转为大写
                else:
                    button.setText(lower)  # 保持小写

        # 更新额外符号按钮
        extra_symbols = {
            "sym1": ("∞", "⊥"),
            "sym2": ("z̄", "‖"),
            "sym3": ("%", "♯"),
            "sym4": ("mod", "♭"),
            "sym5": ("∂", "♮"),
            "sym6": ("!", "♦"),
            "sym7": ("a/b", "♣"),
            "sym8": ("°", "♠")
        }

        for name, (normal, second) in extra_symbols.items():
            button_name = f"pushButton_{name}"
            if hasattr(self.ui, button_name):
                button = getattr(self.ui, button_name)
                if is_second:
                    button.setText(second)
                else:
                    button.setText(normal)

    def on_tab_changed(self, index):
        """标签页切换事件处理"""
        # 获取当前标签页名称
        current_tab = self.ui.tabWidget.widget(index).objectName()

        # 重置当前标签页的2nd模式
        if current_tab in self.second_mode:
            self.second_mode[current_tab] = False

            # 更新按钮显示
            self.update_buttons_for_second_mode(current_tab)

    def on_button_clicked(self, button):
        """按钮点击事件处理"""
        # 获取按钮文本
        text = button.text()

        # 当前标签页
        current_tab = self.ui.tabWidget.currentWidget().objectName()
        is_second = self.second_mode.get(current_tab, False)

        # 根据按钮文本和当前标签页执行不同操作
        # 基本运算
        if text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
            self.add_to_expression(text)
        # 运算符
        elif text in ['+', '-', '×', '÷', '=', '(', ')', '<', '>', '≤', '≥', '≠']:
            if text == '×':
                self.add_to_expression('*')
            elif text == '÷':
                self.add_to_expression('/')
            else:
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
        elif text == 'x²':
            self.add_function("({})**2")
        elif text == '^':
            self.add_to_expression('**')
        elif text == 'log':
            self.add_function("log({}, 10)")  # 以10为底的对数
        elif text == 'ln':
            self.add_function("log({})")  # 自然对数
        # 等于号 - 计算结果
        elif text == '=':
            self.calculate()
        # 三角函数
        elif text in ['sin', 'cos', 'tan', 'cot', 'sec', 'csc']:
            self.add_function(f"{text}({{}})")
        # 反三角函数
        elif text in ['asin', 'acos', 'atan', 'acot', 'asec', 'acsc']:
            self.add_function(f"{text}({{}})")
        # 双曲函数
        elif text in ['sinh', 'cosh', 'tanh']:
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
        # 集合操作
        elif text in ['∩', '∪', '\', '⊂', '⊃', '⊆', '⊇', '∈']:
            if text == '\':  # 差集
                self.add_to_expression('\\')  # 在Python字符串中，\表示一个反斜杠
            else:
                self.add_to_expression(text)
        # 其他符号或字符
        else:
            # 希腊字母映射到sympy符号
            greek_to_sympy = {
                'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta',
                'ε': 'epsilon', 'ζ': 'zeta', 'η': 'eta', 'θ': 'theta',
                'ι': 'iota', 'κ': 'kappa', 'λ': 'lambda', 'μ': 'mu',
                'ν': 'nu', 'ξ': 'xi', 'ο': 'omicron', 'π': 'pi',
                'ρ': 'rho', 'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon',
                'φ': 'phi', 'χ': 'chi', 'ψ': 'psi', 'ω': 'omega',
                'Α': 'Alpha', 'Β': 'Beta', 'Γ': 'Gamma', 'Δ': 'Delta',
                'Ε': 'Epsilon', 'Ζ': 'Zeta', 'Η': 'Eta', 'Θ': 'Theta',
                'Ι': 'Iota', 'Κ': 'Kappa', 'Λ': 'Lambda', 'Μ': 'Mu',
                'Ν': 'Nu', 'Ξ': 'Xi', 'Ο': 'Omicron', 'Π': 'Pi',
                'Ρ': 'Rho', 'Σ': 'Sigma', 'Τ': 'Tau', 'Υ': 'Upsilon',
                'Φ': 'Phi', 'Χ': 'Chi', 'Ψ': 'Psi', 'Ω': 'Omega'
            }

            if text in greek_to_sympy:
                self.add_to_expression(greek_to_sympy[text])
            # 其他字符直接添加
            else:
                self.add_to_expression(text)

    def on_expression_changed(self, text):
        """输入框内容变化时，更新LaTeX显示"""
        self.current_expression = text
        self.update_latex_display()

    def update_latex_display(self):
        """更新LaTeX显示"""
        if not self.current_expression:
            self.web_view.setHtml("<html><body></body></html>")
            return

        try:
            # 尝试使用sympy将表达式转换为LaTeX
            expr = parse_expr(self.current_expression, 
                              local_dict={'x': self.x, 'y': self.y},
                              transformations=self.transformations)
            latex_text = sp.latex(expr)

            # 构建HTML
            html = f"""
            <html>
            <head>
                <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
                <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            </head>
            <body>
                <div style="font-size: 24px; text-align: center; padding: 20px;">
                    $${latex_text}$$
                </div>
            </body>
            </html>
            """
            self.web_view.setHtml(html)
        except Exception as e:
            # 如果解析失败，直接显示原始表达式
            html = f"""
            <html>
            <body>
                <div style="font-size: 16px; text-align: center; padding: 20px;">
                    {self.current_expression}
                </div>
            </body>
            </html>
            """
            self.web_view.setHtml(html)

    def add_to_expression(self, text):
        """向表达式添加文本"""
        cursor_pos = self.expression_input.cursorPosition()
        self.current_expression = (
            self.current_expression[:cursor_pos] +
            text +
            self.current_expression[cursor_pos:]
        )
        self.expression_input.setText(self.current_expression)
        self.expression_input.setCursorPosition(cursor_pos + len(text))

    def add_function(self, template):
        """添加函数，{}将被选中文本替换或光标定位"""
        cursor_pos = self.expression_input.cursorPosition()
        selected_text = self.expression_input.selectedText()

        if selected_text:
            # 如果有选中文本，将其放入函数/表达式中
            new_text = template.format(selected_text)
            self.current_expression = (
                self.current_expression[:self.expression_input.selectionStart()] +
                new_text +
                self.current_expression[self.expression_input.selectionEnd():]
            )
            new_cursor_pos = self.expression_input.selectionStart() + len(new_text)
        else:
            # 无选中文本，光标放在括号内
            placeholder_pos = template.find("{}")
            if placeholder_pos != -1:
                before = template[:placeholder_pos]
                after = template[placeholder_pos+2:]
                self.current_expression = (
                    self.current_expression[:cursor_pos] +
                    before + after +
                    self.current_expression[cursor_pos:]
                )
                new_cursor_pos = cursor_pos + len(before)
            else:
                # 模板中没有{}，直接添加
                self.current_expression = (
                    self.current_expression[:cursor_pos] +
                    template +
                    self.current_expression[cursor_pos:]
                )
                new_cursor_pos = cursor_pos + len(template)

        self.expression_input.setText(self.current_expression)
        self.expression_input.setCursorPosition(new_cursor_pos)

    def calculate(self):
        """计算表达式结果"""
        try:
            if not self.current_expression:
                return

            # 检查是否含有等号，如果有则视为方程
            if "=" in self.current_expression:
                self.solve_equation()
                return

            # 解析并计算表达式
            expr = parse_expr(self.current_expression,
                              local_dict={'x': self.x, 'y': self.y},
                              transformations=self.transformations)
            result = expr

            # 更新显示
            latex_result = sp.latex(result)
            self.update_result_display(latex_result)

            # 添加到历史
            history_item = f"{self.current_expression} = {result}"
            self.add_to_history(history_item)

        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"错误: {str(e)}")

    def update_result_display(self, latex_str):
        """显示计算结果"""
        if not latex_str:
            return

        html = f"""
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
        self.web_view.setHtml(html)

    def add_to_history(self, item):
        """添加计算历史"""
        self.history.append(item)
        # 如果有历史列表控件，也添加到列表
        if hasattr(self, "history_list"):
            self.history_list.addItem(item)

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
            self.update_latex_display()

        except Exception as e:
            QMessageBox.critical(self, "操作错误", f"错误: {str(e)}")

    def solve_equation(self):
        """解方程"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入方程")
                return

            # 检查是否含有等号
            if "=" in self.current_expression:
                left, right = self.current_expression.split("=", 1)
                expr = parse_expr(f"({left})-({right})",
                                 local_dict={'x': self.x, 'y': self.y},
                                 transformations=self.transformations)
            else:
                expr = parse_expr(self.current_expression,
                                 local_dict={'x': self.x, 'y': self.y},
                                 transformations=self.transformations)

            # 解方程
            solutions = sp.solve(expr, self.x)

            if solutions:
                if len(solutions) == 1:
                    result = f"x = {solutions[0]}"
                else:
                    result = "解: " + ", ".join([f"x = {s}" for s in solutions])
            else:
                result = "未找到解"

            # 更新显示
            self.current_expression = result
            self.expression_input.setText(result)
            self.update_latex_display()

        except Exception as e:
            QMessageBox.critical(self, "解方程错误", f"错误: {str(e)}")

    def calculate_derivative(self):
        """计算导数"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            expr = parse_expr(self.current_expression,
                             local_dict={'x': self.x, 'y': self.y},
                             transformations=self.transformations)
            derivative = sp.diff(expr, self.x)

            # 更新显示
            result = f"d/dx({self.current_expression}) = {derivative}"
            self.current_expression = result
            self.expression_input.setText(result)
            self.update_latex_display()

        except Exception as e:
            QMessageBox.critical(self, "计算导数错误", f"错误: {str(e)}")

    def calculate_partial_derivative(self):
        """计算偏导数"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            # 弹出对话框选择变量
            var, ok = QMessageBox.question(
                self, "选择变量", "对哪个变量求偏导数?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            variable = self.x if var == QMessageBox.StandardButton.Yes else self.y
            var_name = 'x' if var == QMessageBox.StandardButton.Yes else 'y'

            expr = parse_expr(self.current_expression,
                             local_dict={'x': self.x, 'y': self.y},
                             transformations=self.transformations)
            partial = sp.diff(expr, variable)

            # 更新显示
            result = f"∂/∂{var_name}({self.current_expression}) = {partial}"
            self.current_expression = result
            self.expression_input.setText(result)
            self.update_latex_display()

        except Exception as e:
            QMessageBox.critical(self, "计算偏导数错误", f"错误: {str(e)}")

    def calculate_integral(self):
        """计算积分"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            expr = parse_expr(self.current_expression,
                             local_dict={'x': self.x, 'y': self.y},
                             transformations=self.transformations)
            integral = sp.integrate(expr, self.x)

            # 更新显示
            result = f"∫{self.current_expression} dx = {integral} + C"
            self.current_expression = result
            self.expression_input.setText(result)
            self.update_latex_display()

        except Exception as e:
            QMessageBox.critical(self, "计算积分错误", f"错误: {str(e)}")

    def calculate_double_integral(self):
        """计算二重积分"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            expr = parse_expr(self.current_expression,
                             local_dict={'x': self.x, 'y': self.y},
                             transformations=self.transformations)
            # 先对x积分，再对y积分
            integral = sp.integrate(sp.integrate(expr, self.x), self.y)

            # 更新显示
            result = f"∬{self.current_expression} dxdy = {integral} + C"
            self.current_expression = result
            self.expression_input.setText(result)
            self.update_latex_display()

        except Exception as e:
            QMessageBox.critical(self, "计算二重积分错误", f"错误: {str(e)}")

    def calculate_mean(self):
        """计算平均值"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析数据
            data = [float(x) for x in data_str.split(",")]

            # 使用sympy计算平均值
            mean_value = sp.stats.mean(data)

            # 更新显示
            result = f"平均值: {mean_value}"
            self.current_expression = result
            self.expression_input.setText(result)
            self.update_latex_display()

        except Exception as e:
            QMessageBox.critical(self, "计算平均值错误", f"错误: {str(e)}")

    def calculate_median(self):
        """计算中位数"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析数据
            data = [float(x) for x in data_str.split(",")]

            # 使用sympy计算中位数
            median_value = sp.stats.median(data)

            # 更新显示
            result = f"中位数: {median_value}"
            self.current_expression = result
            self.expression_input.setText(result)
            self.update_latex_display()

        except Exception as e:
            QMessageBox.critical(self, "计算中位数错误", f"错误: {str(e)}")

    def calculate_std(self):
        """计算标准差"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析数据
            data = [float(x) for x in data_str.split(",")]

            # 使用sympy计算标准差
            std_value = sp.stats.standard_deviation(data)

            # 更新显示
            result = f"标准差: {std_value}"
            self.current_expression = result
            self.expression_input.setText(result)
            self.update_latex_display()

        except Exception as e:
            QMessageBox.critical(self, "计算标准差错误", f"错误: {str(e)}")

# 主应用程序入口
def main():
    app = QApplication(sys.argv)
    calculator = CalculatorApp()
    calculator.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
