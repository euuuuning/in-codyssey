import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class Calculator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.current = "0"      # 현재 입력값
        self.operator = None    # 선택한 연산자
        self.previous = None    # 이전 값
        self.result = None      # 연산 결과

    def input_number(self, num):
        """숫자 입력"""
        if self.current == "0" and num != ".":
            self.current = num
        else:
            # 소수점 중복 방지
            if num == "." and "." in self.current:
                return
            self.current += num

    def set_operator(self, op):
        """연산자 설정"""
        if self.current != "":
            if self.previous is None:
                self.previous = float(self.current)
            else:
                self.equal()  # 이전 계산 실행
                self.previous = float(self.current)
        self.operator = op
        self.current = "0"

    def toggle_sign(self):
        """양수 ↔ 음수 전환"""
        if self.current.startswith("-"):
            self.current = self.current[1:]
        else:
            if self.current != "0":
                self.current = "-" + self.current

    def percent(self):
        """퍼센트 처리"""
        try:
            value = float(self.current)
            self.current = str(value / 100)
        except:
            self.current = "Error"

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError
        return a / b

    def equal(self):
        """결과 계산"""
        try:
            if self.operator and self.previous is not None:
                a = float(self.previous)
                b = float(self.current)
                if self.operator == "+":
                    self.result = self.add(a, b)
                elif self.operator == "−":
                    self.result = self.subtract(a, b)
                elif self.operator == "×":
                    self.result = self.multiply(a, b)
                elif self.operator == "÷":
                    self.result = self.divide(a, b)
                else:
                    return

                # 숫자 범위 제한
                if abs(self.result) > 1e18:
                    raise OverflowError

                # 정수인 경우 소수점 제거
                if self.result == int(self.result):
                    self.result = int(self.result)

                self.current = str(self.result)
                self.previous = None
                self.operator = None

        except ZeroDivisionError:
            self.current = "Error"
            self.reset()
        except OverflowError:
            self.current = "Error"
            self.reset()
        except:
            self.current = "Error"
            self.reset()


class CalculatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iPhone Style Calculator")
        self.setFixedSize(360, 550)
        self.setStyleSheet("background-color: black;")
        self.calc = Calculator()
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()
        vbox.setContentsMargins(15, 20, 15, 15)
        vbox.setSpacing(10)
        self.setLayout(vbox)

        # 디스플레이
        self.display = QLineEdit("0")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFont(QFont("Helvetica Neue", 48, QFont.Weight.Light))
        self.display.setStyleSheet("""
            background-color: black;
            color: white;
            border: none;
            padding: 15px;
        """)
        self.display.setReadOnly(True)
        vbox.addWidget(self.display)

        # 버튼 레이아웃
        grid = QGridLayout()
        grid.setSpacing(10)
        vbox.addLayout(grid)

        buttons = [
            ["AC", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["0", ".", "="]
        ]

        row = 0
        for btn_row in buttons:
            col = 0
            for btn_text in btn_row:
                button = QPushButton(btn_text)
                button.setFont(QFont("Helvetica Neue", 24))
                button.setFixedHeight(80)

                if btn_text == "0":
                    button.setFixedWidth(160)
                    grid.addWidget(button, row + 1, col, 1, 2)
                    col += 1
                else:
                    button.setFixedWidth(80)
                    grid.addWidget(button, row + 1, col, 1, 1)

                # 색상 스타일
                if btn_text in ["÷", "×", "−", "+", "="]:
                    button.setStyleSheet("""
                        background-color: #FF9F0A;
                        color: white;
                        border-radius: 40px;
                    """)
                elif btn_text in ["AC", "+/-", "%"]:
                    button.setStyleSheet("""
                        background-color: #A5A5A5;
                        color: black;
                        border-radius: 40px;
                    """)
                else:
                    button.setStyleSheet("""
                        background-color: #333333;
                        color: white;
                        border-radius: 40px;
                    """)

                button.clicked.connect(self.on_button_click)
                col += 1
            row += 1

    def on_button_click(self):
        sender = self.sender()
        text = sender.text()

        if text == "AC":
            self.calc.reset()
        elif text == "+/-":
            self.calc.toggle_sign()
        elif text == "%":
            self.calc.percent()
        elif text in ["+", "−", "×", "÷"]:
            self.calc.set_operator(text)
        elif text == "=":
            self.calc.equal()
        elif text == ".":
            self.calc.input_number(".")
        else:
            self.calc.input_number(text)

        self.display.setText(self.calc.current)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = CalculatorUI()
    calc.show()
    sys.exit(app.exec())
