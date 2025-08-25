import sys
import math
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 기존 Calculator 클래스
class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setFixedSize(360, 520)
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.display = QLineEdit("0")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFont(QFont("Arial", 32))
        self.display.setReadOnly(True)
        self.display.setStyleSheet("background-color: black; color: white; border: none; padding: 10px;")
        vbox.addWidget(self.display)

    def input_number(self, value):
        current = self.display.text()
        if current == "0":
            self.display.setText(value)
        else:
            self.display.setText(current + value)

    def clear(self):
        self.display.setText("0")

# EngineeringCalculator 클래스
class EngineeringCalculator(Calculator):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iPhone Engineering Calculator")
        self.setFixedSize(700, 420)
        self.add_engineering_buttons()

    def add_engineering_buttons(self):
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        self.layout().addLayout(grid)

        buttons = [
            ["2nd", "π", "e", "AC", "+/-", "%", "÷"],
            ["x²", "x³", "xʸ", "7", "8", "9", "×"],
            ["√", "x!", "ln", "4", "5", "6", "−"],
            ["sin", "cos", "tan", "1", "2", "3", "+"],
            ["sinh", "cosh", "tanh", "0", ".", "=", ""]
        ]

        for row, row_buttons in enumerate(buttons):
            col = 0
            for btn_text in row_buttons:
                if btn_text == "":
                    col += 1
                    continue

                button = QPushButton(btn_text)
                button.setFont(QFont("Helvetica Neue", 18))
                button.setFixedSize(78, 60)

                # 아이폰 스타일 색상
                if btn_text in ["÷", "×", "−", "+", "="]:
                    button.setStyleSheet("background-color: #FF9F0A; color: white; border-radius: 30px;")
                elif btn_text in ["AC", "+/-", "%"]:
                    button.setStyleSheet("background-color: #A5A5A5; color: black; border-radius: 30px;")
                elif btn_text in ["2nd", "π", "e", "x²", "x³", "xʸ", "√", "x!", "ln",
                                  "sin", "cos", "tan", "sinh", "cosh", "tanh"]:
                    button.setStyleSheet("background-color: #505050; color: white; border-radius: 30px;")
                else:
                    button.setStyleSheet("background-color: #333333; color: white; border-radius: 30px;")

                button.clicked.connect(lambda checked, text=btn_text: self.on_button_click(text))

                if btn_text == "0":
                    button.setFixedWidth(162)
                    grid.addWidget(button, row, col, 1, 2)
                    col += 1
                else:
                    grid.addWidget(button, row, col, 1, 1)

                col += 1

    def on_button_click(self, text):
        try:
            if text == "AC":
                self.clear()
            elif text == "π":
                self.display.setText(str(math.pi))
            elif text == "x²":
                self.square()
            elif text == "x³":
                self.cube()
            elif text == "sin":
                self.sin()
            elif text == "cos":
                self.cos()
            elif text == "tan":
                self.tan()
            elif text == "sinh":
                self.sinh()
            elif text == "cosh":
                self.cosh()
            elif text == "tanh":
                self.tanh()
            elif text.isdigit() or text == ".":
                self.input_number(text)
            else:
                pass
        except Exception:
            self.display.setText("Error")

    # 공학용 기능 구현
    def square(self):
        value = float(self.display.text())
        self.display.setText(str(value ** 2))

    def cube(self):
        value = float(self.display.text())
        self.display.setText(str(value ** 3))

    def sin(self):
        value = float(self.display.text())
        self.display.setText(str(math.sin(math.radians(value))))

    def cos(self):
        value = float(self.display.text())
        self.display.setText(str(math.cos(math.radians(value))))

    def tan(self):
        value = float(self.display.text())
        if (value % 180) == 90:
            self.display.setText("Error")
        else:
            self.display.setText(str(math.tan(math.radians(value))))

    def sinh(self):
        value = float(self.display.text())
        self.display.setText(str(math.sinh(value)))

    def cosh(self):
        value = float(self.display.text())
        self.display.setText(str(math.cosh(value)))

    def tanh(self):
        value = float(self.display.text())
        self.display.setText(str(math.tanh(value)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = EngineeringCalculator()
    calc.show()
    sys.exit(app.exec())
