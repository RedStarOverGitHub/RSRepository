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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')


class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kalculate")
        self.setGeometry(100, 100, 1000, 700)

        # 初始化符号变量
        self.x, self.y = sp.symbols('x y')
        self.current_expression = ""
        self.history = []
        self.transformations = standard_transformations + (implicit_multiplication_application,)

        # 角度制设置，默认为弧度制
        self.angle_mode = "RAD"  # 可选值："DEG"(角度制) 或 "RAD"(弧度制)

        # 创建主部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 主布局
        self.main_layout = QVBoxLayout(self.central_widget)

        # 创建显示区域
        self.create_display_area()

        # 创建标签页
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # 创建标签页内容
        self.create_tabs()

        # 创建控制按钮
        self.create_control_buttons()

        # 创建菜单
        self.create_menus()

        # 连接标签页切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.show()  # 显示主窗口

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
