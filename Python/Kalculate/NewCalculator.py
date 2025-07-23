import sys
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QTabWidget, QPushButton, QLabel,
                              QListWidget, QMenuBar, QMenu, QGridLayout,
                              QLineEdit, QMessageBox, QFileDialog, QSplitter,
                              QSizePolicy, QInputDialog)
from PySide6.QtCore import Qt, Signal, Slot, QFile
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')

class CalculatorApp(QMainWindow):
    """基于qtUI.ui的科学计算器应用"""

    def __init__(self):
        super().__init__()

        # 加载UI文件
        loader = QUiLoader()
        qtui = QFile(".\\Python/Kalculate/qtUI.ui")
        qtui.open(QFile.ReadOnly)
        self.ui = loader.load(qtui)
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

        # 显示主窗口
        self.show()

    def setup_ui_connections(self):
        """设置UI元素和连接信号"""
        # 输入框
        self.expression_input = self.ui.lineEdit
        self.expression_input.textChanged.connect(self.on_expression_changed)
        self.expression_input.returnPressed.connect(self.calculate)

        # 统计页面输入框
        self.stats_input = self.ui.lineEdit_num

        # LaTeX显示视图初始化
        self.web_view = self.ui.webEngineView
        self.init_latex_display()

        # 连接所有标签页的切换信号
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)

        # 连接所有按钮
        self.connect_all_buttons()

    def init_latex_display(self):
        """初始化LaTeX显示"""
        empty_html = """
        <html>
        <head>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        </head>
        <body>
            <div style="font-size: 24px; text-align: center; padding: 20px;">
                <p>输入表达式进行计算</p>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(empty_html)

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

    def on_button_clicked(self, button):
        """按钮点击事件处理"""
        try:
            # 获取按钮文本
            text = button.text()

            # 当前标签页
            current_tab = self.ui.tabWidget.currentWidget().objectName()
            is_second = self.second_mode.get(current_tab, False)

            # 数字和基本运算符
            if text in '0123456789.':
                self.add_to_expression(text)
            elif text in '+-':
                self.add_to_expression(text)
            elif text == '×':
                self.add_to_expression('*')
            elif text == '÷':
                self.add_to_expression('/')
            elif text == '^':
                self.add_to_expression('**')
            elif text in '()=<>≤≥≠':
                self.add_to_expression(text)
            # 特殊符号和常数
            elif text == 'π':
                self.add_to_expression('pi')
            elif text == 'e' or text == 'E':
                self.add_to_expression('E')
            elif text == 'i' or text == 'I':
                self.add_to_expression('I')  # sympy使用I表示虚数单位
            # 基本函数
            elif text == '√':
                self.insert_sqrt()
            elif text == 'x²':  # 2nd模式下的平方
                self.add_function("({})**2")
            elif text == 'log':
                self.insert_log()
            elif text == 'ln':  # 2nd模式下的自然对数
                self.add_function("log({})")
            # 三角函数和反三角函数
            elif text in ['sin', 'cos', 'tan', 'cot', 'sec', 'csc',
                         'asin', 'acos', 'atan', 'acot', 'asec', 'acsc',
                         'sinh', 'cosh', 'tanh']:
                self.insert_trig_function(text)
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
            # Answer按钮
            elif text == 'Answer':
                self.insert_answer()
            # 正负号切换
            elif text == '+/-':
                self.toggle_sign()
            # 等号计算
            elif text == '=':
                self.calculate()
            # 统计函数
            elif text == 'x̅' or text == 'E(X)':  # 平均值或期望值
                self.calculate_mean()
            elif text == 'x̃':  # 中位数
                self.calculate_median()
            elif text == 'σ':  # 标准差
                self.calculate_std()
            elif text == 'σ²':  # 方差
                self.calculate_variance()
            elif text == 'gcd':  # 最大公约数
                self.calculate_gcd()
            elif text == 'lcm':  # 最小公倍数
                self.calculate_lcm()
            elif text == 'max':  # 最大值
                self.calculate_max()
            elif text == 'min':  # 最小值
                self.calculate_min()
            # 矩阵/集合运算
            elif text in '[]{}⟨⟩|∈∩∪\\⊂⊃⊆⊇∀∃△∅#':
                self.add_to_expression(text)
            # 字母按钮 - 直接添加到表达式
            elif len(text) == 1 and text.isalpha():
                # 如果是单个字母，直接添加
                self.add_to_expression(text)
            else:
                # 特殊转换为sympy识别的符号
                sympy_replacements = {
                    'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta',
                    'ε': 'epsilon', 'ζ': 'zeta', 'η': 'eta', 'θ': 'theta',
                    'ι': 'iota', 'κ': 'kappa', 'λ': 'lambda', 'μ': 'mu',
                    'ν': 'nu', 'ξ': 'xi', 'ο': 'omicron', 'π': 'pi',
                    'ρ': 'rho', 'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon',
                    'φ': 'phi', 'χ': 'chi', 'ψ': 'psi', 'ω': 'omega',
                    # 大写希腊字母也映射到相应的符号
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
                    # 其他按钮，尝试直接添加到表达式
                    self.add_to_expression(text)
        except Exception as e:
            # 捕获并显示错误，防止应用崩溃
            QMessageBox.critical(self, "按钮处理错误", f"处理按钮时发生错误: {str(e)}")

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

    def on_tab_changed(self, index):
        """标签页切换事件处理"""
        # 获取当前标签页名称
        current_tab = self.ui.tabWidget.widget(index).objectName()

        # 重置2nd模式状态
        if current_tab in self.second_mode:
            self.second_mode[current_tab] = False
            self.update_buttons_for_second_mode(current_tab)

    def add_to_expression(self, text):
        """向表达式添加文本"""
        cursor_pos = self.expression_input.cursorPosition()
        new_expression = (
            self.current_expression[:cursor_pos] +
            text +
            self.current_expression[cursor_pos:]
        )
        self.current_expression = new_expression
        self.expression_input.setText(new_expression)
        self.expression_input.setCursorPosition(cursor_pos + len(text))

    def add_function(self, template):
        """添加一个函数，保留一个占位符{}用于插入函数参数"""
        cursor_pos = self.expression_input.cursorPosition()
        selected_text = self.expression_input.selectedText()

        if selected_text:
            # 如果有选中文本，将其作为函数参数
            func_text = template.format(selected_text)
            self.current_expression = (
                self.current_expression[:self.expression_input.selectionStart()] +
                func_text +
                self.current_expression[self.expression_input.selectionEnd():]
            )
            new_cursor_pos = self.expression_input.selectionStart() + len(func_text)
        else:
            # 如果没有选中文本，添加函数名和括号，光标放在括号内
            placeholder = ""
            func_text = template.format(placeholder)

            # 找到括号内位置以放置光标
            open_pos = func_text.find("(")
            close_pos = func_text.find(")")

            if open_pos >= 0 and close_pos >= 0:
                # 将光标放在括号内
                self.current_expression = (
                    self.current_expression[:cursor_pos] +
                    func_text +
                    self.current_expression[cursor_pos:]
                )
                new_cursor_pos = cursor_pos + open_pos + 1
            else:
                # 如果找不到括号，就放在末尾
                self.current_expression = (
                    self.current_expression[:cursor_pos] +
                    func_text +
                    self.current_expression[cursor_pos:]
                )
                new_cursor_pos = cursor_pos + len(func_text)

        self.expression_input.setText(self.current_expression)
        self.expression_input.setCursorPosition(new_cursor_pos)

    def calculate(self):
        """用sympy解析并计算表达式"""
        try:
            if not self.current_expression:
                return

            # 去除表达式末尾的等号（如果有）
            expression = self.current_expression
            if expression.endswith('='):
                expression = expression[:-1].strip()

            # 替换显示符号为sympy可识别的符号
            expression = expression.replace('×', '*').replace('÷', '/')

            # 在角度制模式下处理三角函数
            if self.angle_mode == "DEG":
                # 替换三角函数调用，添加角度转弧度的转换
                if 'sin(' in expression:
                    expression = expression.replace('sin(', 'sin(pi/180*')
                if 'cos(' in expression:
                    expression = expression.replace('cos(', 'cos(pi/180*')
                if 'tan(' in expression:
                    expression = expression.replace('tan(', 'tan(pi/180*')
                # 反三角函数结果需要从弧度转为角度
                if 'asin(' in expression:
                    expression = expression.replace('asin(', '(180/pi)*asin(')
                if 'acos(' in expression:
                    expression = expression.replace('acos(', '(180/pi)*acos(')
                if 'atan(' in expression:
                    expression = expression.replace('atan(', '(180/pi)*atan(')

            # 解析并计算表达式
            expr = parse_expr(expression, 
                             local_dict={'x': self.x, 'y': self.y, 'z': self.z, 'pi': sp.pi, 'E': sp.E, 'I': sp.I},
                             transformations=self.transformations)

            # 使用sympy进行计算
            result = expr.evalf()

            # 保存结果，以便后续使用
            self.last_answer = result

            # 转换为LaTeX格式显示
            latex_result = sp.latex(result)
            self.update_result_latex_display(latex_result)

            # 添加到历史记录
            history_item = f"{self.current_expression} = {result}"
            self.add_to_history(history_item)

            return result
        except Exception as e:
            error_msg = str(e)
            self.update_result_latex_display(f"\text{{Error: {error_msg}}}")
            QMessageBox.warning(self, "计算错误", f"计算出错: {error_msg}")
            return None

    def update_result_latex_display(self, latex_str):
        """以LaTeX格式显示结果"""
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
        self.web_view.setHtml(latex_html)

    def on_expression_changed(self, text):
        """处理表达式输入变化"""
        self.current_expression = text

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
        if hasattr(self.ui, "pushButton_hyp"):
            is_hyp_mode = self.ui.pushButton_hyp.styleSheet() != ""
        else:
            is_hyp_mode = False

        if is_second:
            # 在2nd模式下为反三角函数
            if is_hyp_mode:
                # 反双曲函数
                self.add_function(f"a{func_name}h({{}})")
            else:
                # 反三角函数
                self.add_function(f"a{func_name}({{}})")
        else:
            if is_hyp_mode:
                # 双曲函数
                self.add_function(f"{func_name}h({{}})")
            else:
                # 普通三角函数
                self.add_function(f"{func_name}({{}})")

    def toggle_hyperbolic(self):
        """切换双曲函数模式"""
        if hasattr(self.ui, "pushButton_hyp"):
            hyp_button = self.ui.pushButton_hyp
            is_hyp_mode = hyp_button.styleSheet() != ""

            if is_hyp_mode:
                hyp_button.setStyleSheet("")
            else:
                hyp_button.setStyleSheet("background-color: lightgreen;")

    def calculate_derivative(self):
        """计算导数"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            expr = parse_expr(self.current_expression, 
                             local_dict={'x': self.x, 'y': self.y, 'z': self.z},
                             transformations=self.transformations)
            derivative = sp.diff(expr, self.x)

            result = f"d/dx {self.current_expression} = {derivative}"
            self.expression_input.setText(result)
            self.current_expression = result

            # 显示LaTeX结果
            latex_result = sp.latex(derivative)
            self.update_result_latex_display(latex_result)

            # 添加到历史记录
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "导数计算错误", f"错误: {str(e)}")

    def calculate_partial_derivative(self):
        """计算偏导数"""
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

                # 显示LaTeX结果
                latex_result = sp.latex(derivative)
                self.update_result_latex_display(latex_result)

                # 添加到历史记录
                self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "偏导数计算错误", f"错误: {str(e)}")

    def calculate_integral(self):
        """计算积分"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            expr = parse_expr(self.current_expression, 
                             local_dict={'x': self.x, 'y': self.y, 'z': self.z},
                             transformations=self.transformations)
            integral = sp.integrate(expr, self.x)

            result = f"∫{self.current_expression} dx = {integral} + C"
            self.expression_input.setText(result)
            self.current_expression = result

            # 显示LaTeX结果
            latex_result = sp.latex(integral) + " + C"
            self.update_result_latex_display(latex_result)

            # 添加到历史记录
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "积分计算错误", f"错误: {str(e)}")

    def calculate_double_integral(self):
        """计算二重积分"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            # 询问用户积分变量
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

            # 显示LaTeX结果
            latex_result = sp.latex(double_integral) + " + C"
            self.update_result_latex_display(latex_result)

            # 添加到历史记录
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "二重积分计算错误", f"错误: {str(e)}")

    def apply_operation(self, operation):
        """应用SymPy操作如factor, expand, simplify等"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入表达式")
                return

            expr = parse_expr(self.current_expression,
                             local_dict={'x': self.x, 'y': self.y, 'z': self.z},
                             transformations=self.transformations)
            result = operation(expr)

            self.expression_input.setText(str(result))
            self.current_expression = str(result)

            # 显示LaTeX结果
            latex_result = sp.latex(result)
            self.update_result_latex_display(latex_result)

            # 添加到历史记录
            self.add_to_history(f"{self.current_expression} = {result}")
        except Exception as e:
            QMessageBox.critical(self, "操作错误", f"错误: {str(e)}")

    def solve_equation(self):
        """解方程"""
        try:
            if not self.current_expression:
                QMessageBox.warning(self, "输入错误", "请先输入方程")
                return

            # 询问用户解方程的变量
            var_name, ok = QInputDialog.getText(self, "解方程", "对哪个变量解方程? (默认为x)")
            if ok:
                if not var_name:
                    var_name = 'x'

                var = sp.Symbol(var_name)
                expr = parse_expr(self.current_expression, 
                                 local_dict={'x': self.x, 'y': self.y, 'z': self.z},
                                 transformations=self.transformations)
                solutions = sp.solve(expr, var)

                if solutions:
                    if len(solutions) == 1:
                        result = f"{var_name} = {solutions[0]}"
                    else:
                        result = f"{var_name} = {solutions}"
                else:
                    result = "无解"

                self.expression_input.setText(result)
                self.current_expression = result

                # 显示LaTeX结果
                latex_result = f"{var_name} = {sp.latex(solutions)}"
                self.update_result_latex_display(latex_result)

                # 添加到历史记录
                self.add_to_history(f"解方程 {self.current_expression}: {result}")
        except Exception as e:
            QMessageBox.critical(self, "解方程错误", f"错误: {str(e)}")

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
            mean_value = sum(data) / len(data)

            result = f"Mean: {mean_value}"
            self.expression_input.setText(result)
            self.current_expression = result

            # 显示LaTeX结果
            self.update_result_latex_display(str(mean_value))

            # 添加到历史记录
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "平均值计算错误", f"错误: {str(e)}")

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
            sorted_data = sorted(data)
            n = len(sorted_data)
            if n % 2 == 0:
                median_value = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
            else:
                median_value = sorted_data[n//2]

            result = f"Median: {median_value}"
            self.expression_input.setText(result)
            self.current_expression = result

            # 显示LaTeX结果
            self.update_result_latex_display(str(median_value))

            # 添加到历史记录
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "中位数计算错误", f"错误: {str(e)}")

    def calculate_std(self):
        """计算标准差"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析数据
            data = [float(x) for x in data_str.split(",")]

            # 使用numpy计算标准差
            std_value = np.std(data)

            result = f"Std: {std_value}"
            self.expression_input.setText(result)
            self.current_expression = result

            # 显示LaTeX结果
            self.update_result_latex_display(str(std_value))

            # 添加到历史记录
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "标准差计算错误", f"错误: {str(e)}")

    def calculate_variance(self):
        """计算方差"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析数据
            data = [float(x) for x in data_str.split(",")]

            # 使用numpy计算方差
            var_value = np.var(data)

            result = f"Variance: {var_value}"
            self.expression_input.setText(result)
            self.current_expression = result

            # 显示LaTeX结果
            self.update_result_latex_display(str(var_value))

            # 添加到历史记录
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "方差计算错误", f"错误: {str(e)}")

    def calculate_gcd(self):
        """计算最大公约数"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析数据
            data = [int(float(x)) for x in data_str.split(",")]

            # 使用sympy计算最大公约数
            gcd_result = data[0]
            for i in range(1, len(data)):
                gcd_result = sp.gcd(gcd_result, data[i])

            result = f"GCD: {gcd_result}"
            self.expression_input.setText(result)
            self.current_expression = result

            # 显示LaTeX结果
            self.update_result_latex_display(str(gcd_result))

            # 添加到历史记录
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "GCD计算错误", f"错误: {str(e)}")

    def calculate_lcm(self):
        """计算最小公倍数"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析数据
            data = [int(float(x)) for x in data_str.split(",")]

            # 使用sympy计算最小公倍数
            lcm_result = data[0]
            for i in range(1, len(data)):
                lcm_result = sp.lcm(lcm_result, data[i])

            result = f"LCM: {lcm_result}"
            self.expression_input.setText(result)
            self.current_expression = result

            # 显示LaTeX结果
            self.update_result_latex_display(str(lcm_result))

            # 添加到历史记录
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "LCM计算错误", f"错误: {str(e)}")

    def calculate_max(self):
        """计算最大值"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析数据
            data = [float(x) for x in data_str.split(",")]
            max_value = max(data)

            result = f"Max: {max_value}"
            self.expression_input.setText(result)
            self.current_expression = result

            # 显示LaTeX结果
            self.update_result_latex_display(str(max_value))

            # 添加到历史记录
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "Max计算错误", f"错误: {str(e)}")

    def calculate_min(self):
        """计算最小值"""
        try:
            data_str = self.stats_input.text()
            if not data_str:
                QMessageBox.warning(self, "输入错误", "请先输入数据")
                return

            # 解析数据
            data = [float(x) for x in data_str.split(",")]
            min_value = min(data)

            result = f"Min: {min_value}"
            self.expression_input.setText(result)
            self.current_expression = result

            # 显示LaTeX结果
            self.update_result_latex_display(str(min_value))

            # 添加到历史记录
            self.add_to_history(result)
        except Exception as e:
            QMessageBox.critical(self, "Min计算错误", f"错误: {str(e)}")

    def insert_answer(self):
        """插入上一个计算结果"""
        if hasattr(self, "last_answer"):
            self.add_to_expression(str(self.last_answer))
        else:
            QMessageBox.information(self, "提示", "当前没有可用的计算结果")

    def toggle_sign(self):
        """切换表达式的正负号"""
        cursor_pos = self.expression_input.cursorPosition()
        selected_text = self.expression_input.selectedText()

        if selected_text:
            # 对选中文本取反
            new_text = f"(-1)*({selected_text})"
            self.current_expression = (
                self.current_expression[:self.expression_input.selectionStart()] +
                new_text +
                self.current_expression[self.expression_input.selectionEnd():]
            )
            new_cursor_pos = self.expression_input.selectionStart() + len(new_text)
        else:
            # 添加(-1)*在光标位置
            new_text = "(-1)*"
            self.current_expression = (
                self.current_expression[:cursor_pos] +
                new_text +
                self.current_expression[cursor_pos:]
            )
            new_cursor_pos = cursor_pos + len(new_text)

        self.expression_input.setText(self.current_expression)
        self.expression_input.setCursorPosition(new_cursor_pos)

    def add_to_history(self, item):
        """添加项目到历史记录"""
        self.history.append(item)
        if hasattr(self.ui, "history_list"):
            self.ui.history_list.addItem(item)

# 应用入口
def main():
    app = QApplication(sys.argv)
    calculator = CalculatorApp()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
