# -*- coding: utf-8 -*-
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iPhone Calculator")
        self.setFixedSize(360, 550)
        self.initUI()

    def initUI(self):
        # --- 수식 표시창 ---
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(80)
        self.display.setStyleSheet("background-color: black; color: white; font-size: 40px; padding: 10px;")
        self.display.setFont(QFont('Arial', 30))

        # --- 버튼 레이아웃 ---
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(10)
        # 버튼 정의: text, row, col, colspan(optional)
        buttons = [
            [('AC', 'func'), ('+/-', 'func'), ('%', 'func'), ('÷', 'op')],
            [('7', 'num'), ('8', 'num'), ('9', 'num'), ('×', 'op')],
            [('4', 'num'), ('5', 'num'), ('6', 'num'), ('-', 'op')],
            [('1', 'num'), ('2', 'num'), ('3', 'num'), ('+', 'op')],
            [('0', 'num', 2), ('.', 'num'), ('=', 'op')]
        ]

        for row, row_values in enumerate(buttons):
            col = 0
            for item in row_values:
                text = item[0]
                btype = item[1]
                colspan = item[2] if len(item) > 2 else 1

                button = QPushButton(text)
                button.setFixedSize(80*colspan, 80)
                button.setFont(QFont('Arial', 24))
                button.setStyleSheet(self.get_button_style(btype))
                button.clicked.connect(self.button_clicked)
                buttons_layout.addWidget(button, row, col, 1, colspan)
                col += colspan

        # --- 메인 레이아웃 ---
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.addWidget(self.display)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def get_button_style(self, btype):
        if btype == 'num':
            return "background-color: #333333; color: white; border-radius: 40px;"
        elif btype == 'op':
            return "background-color: orange; color: white; border-radius: 40px;"
        elif btype == 'func':
            return "background-color: #a5a5a5; color: black; border-radius: 40px;"
        return ""

    def button_clicked(self):
        sender = self.sender()
        text = sender.text()
        # 숫자 및 점 입력
        if text in '0123456789.':
            current = self.display.text()
            self.display.setText(current + text)
        elif text == 'AC':
            self.display.clear()
        else:
            # 연산자/기능 버튼 이벤트는 보너스 과제에서 구현
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())
