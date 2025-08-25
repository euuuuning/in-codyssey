import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class EngineeringCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iPhone Engineering Calculator")
        self.setFixedSize(700, 420)  # 가로형 비율
        self.setStyleSheet("background-color: black;")
        self.init_ui()

    def init_ui(self):
        # 메인 레이아웃
        vbox = QVBoxLayout()
        vbox.setContentsMargins(25, 20, 25, 20)  # 좌우상하 여백 확대
        vbox.setSpacing(20)  # 디스플레이와 버튼 간격 넓힘
        self.setLayout(vbox)

        # 디스플레이
        self.display = QLineEdit("0")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFont(QFont("Helvetica Neue", 36, QFont.Weight.Light))
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
        grid.setSpacing(35)  # 버튼 간격 넓힘
        vbox.addLayout(grid)

        # 아이폰 공학용 계산기 버튼 구성
        buttons = [
            ["2nd", "π", "e", "AC", "+/-", "%", "÷"],
            ["x²", "x³", "xʸ", "7", "8", "9", "×"],
            ["√", "x!", "ln", "4", "5", "6", "−"],
            ["sin", "cos", "tan", "1", "2", "3", "+"],
            ["log", "(", ")", "0", ".", "=", ""]
        ]

        # 버튼 생성
        row = 0
        for btn_row in buttons:
            col = 0
            for btn_text in btn_row:
                if btn_text == "":
                    col += 1
                    continue

                button = QPushButton(btn_text)
                button.setFont(QFont("Helvetica Neue", 18))
                button.setFixedSize(78, 60)  # 버튼 크기 조정

                # 버튼 스타일 적용
                if btn_text in ["÷", "×", "−", "+", "="]:
                    button.setStyleSheet("""
                        background-color: #FF9F0A;
                        color: white;
                        border-radius: 30px;
                    """)
                elif btn_text in ["AC", "+/-", "%"]:
                    button.setStyleSheet("""
                        background-color: #A5A5A5;
                        color: black;
                        border-radius: 30px;
                    """)
                elif btn_text in [
                    "2nd", "π", "e", "x²", "x³", "xʸ", "√", "x!", "ln",
                    "log", "sin", "cos", "tan", "(", ")"
                ]:
                    button.setStyleSheet("""
                        background-color: #505050;
                        color: white;
                        border-radius: 30px;
                    """)
                else:
                    button.setStyleSheet("""
                        background-color: #333333;
                        color: white;
                        border-radius: 30px;
                    """)

                # 이벤트 연결
                button.clicked.connect(self.on_button_click)

                # 5행의 "0" 버튼은 두 칸 차지
                if btn_text == "0":
                    button.setFixedWidth(162)
                    grid.addWidget(button, row + 1, col, 1, 2)
                    col += 1
                else:
                    grid.addWidget(button, row + 1, col, 1, 1)

                col += 1
            row += 1

    def on_button_click(self):
        """버튼 클릭 시 디스플레이에 입력"""
        sender = self.sender()
        text = sender.text()

        # AC 버튼 → 초기화
        if text == "AC":
            self.display.setText("0")
        else:
            current = self.display.text()
            if current == "0":
                self.display.setText(text)
            else:
                self.display.setText(current + text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = EngineeringCalculator()
    calc.show()
    sys.exit(app.exec())
