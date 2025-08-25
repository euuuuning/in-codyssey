import sys, math, random
from functools import partial
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

ORANGE = "#FF9F0A"    # 연산자
LIGHT  = "#A5A5A5"    # 보조(AC, +/-, %)
MID    = "#505050"    # 공학 버튼
DARK   = "#333333"    # 숫자

class IOSCalc(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iPhone Engineering Calculator (PyQt6)")
        self.setStyleSheet("background:#000;")
        self.setFixedSize(640, 420)

        self.is_second = False
        self.angle_mode = "Rad"  # "Deg" 또는 "Rad"
        self.memory = 0.0

        self.pending = ""  # 표현식 모드로도 쓸 수 있게 문자열 유지

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setSpacing(10)
        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFont(QFont("Arial", 36))
        self.display.setStyleSheet("QLineEdit{background:#000;color:#fff;border:none;padding:6px 10px;}")
        v.addWidget(self.display)

        g = QGridLayout()
        g.setHorizontalSpacing(10)
        g.setVerticalSpacing(10)
        v.addLayout(g)
        self.grid = g

        # 버튼 텍스트를 iOS 공학용 배치로 구성
        self.layout_map = [
            ["(", ")", "mc", "m+", "m-", "mr", "AC", "+/-", "%", "÷"],
            ["2nd","x²","x³","xʸ","eˣ","10ˣ","7","8","9","×"],
            ["1/x","²√x","³√x","ʸ√x","ln","log₁₀","4","5","6","−"],
            ["x!","sin","cos","tan","e","EE","1","2","3","+"],
            ["Deg","sinh","cosh","tanh","π","Rand","0",".","⌫","="],
        ]

        self.btn_refs = {}  # 토글에 사용할 버튼 참조 저장

        for row, row_items in enumerate(self.layout_map):
            for col, label in enumerate(row_items):
                btn = QPushButton(label)
                btn.setFont(QFont("Arial", 18))
                btn.setFixedSize(56, 56)
                btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                btn.setStyleSheet(self._style_for(label))
                btn.clicked.connect(partial(self.on_click, label))
                g.addWidget(btn, row, col)
                self.btn_refs[label] = btn
        
        # Rad 버튼이 사라졌으므로 초기 Deg 버튼 텍스트를 현재 모드(Rad)로 설정
        self.btn_refs["Deg"].setText(self.angle_mode)

        # 0 버튼 가로 확장(iOS 느낌)
        self.btn_refs["0"].setFixedWidth(122)
        
    def _style_for(self, text: str) -> str:
        radius = 28
        base = "QPushButton{border:none;border-radius:%dpx;font-weight:500;}" % radius
        if text in {"÷","×","−","+","="}:
            return base + f"QPushButton{{background:{ORANGE};color:#fff;}}"
        if text in {"AC","+/-","%"}:
            return base + f"QPushButton{{background:{LIGHT};color:#000;}}"
        if text in {"0","1","2","3","4","5","6","7","8","9",".","⌫"}:
            return base + f"QPushButton{{background:{DARK};color:#fff;}}"
        # 나머지는 공학 버튼
        return base + f"QPushButton{{background:{MID};color:#fff;}}"

    # ---------- 유틸 ----------
    def _get_value(self) -> float:
        try:
            return float(self.display.text())
        except Exception:
            # π, e 등 들어있을 수 있으니 안전 파싱
            txt = self._to_python_expr(self.display.text())
            try:
                return float(eval(txt, self._safe_env()))
            except Exception:
                return 0.0

    def _set_value(self, value):
        # 너무 긴 소수는 iOS처럼 깔끔하게
        if isinstance(value, float):
            s = f"{value:.12g}"
        else:
            s = str(value)
        self.display.setText(s)

    def _to_python_expr(self, s: str) -> str:
        # 화면 문자열을 eval 가능한 파이썬 표현으로 변환
        rep = (
            ("÷","/"),
            ("×","*"),
            ("−","-"),
            ("^","**"),
            ("π", str(math.pi)),
            ("e", str(math.e)),
            ("EE","e"),  # 지수 표기
        )
        for a,b in rep:
            s = s.replace(a,b)
        return s

    def _safe_env(self):
        # eval에 사용할 안전한 환경 (필요한 것만 노출)
        return {
            "__builtins__": {},
            "pi": math.pi,
            "e": math.e,
            "sqrt": math.sqrt,
            "abs": abs,
            "sin": lambda x: math.sin(self._rad(x)),
            "cos": lambda x: math.cos(self._rad(x)),
            "tan": lambda x: math.tan(self._rad(x)),
            "asin": lambda x: self._ang(math.asin(x)),
            "acos": lambda x: self._ang(math.acos(x)),
            "atan": lambda x: self._ang(math.atan(x)),
            "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
            "log": math.log, "log10": math.log10, "exp": math.exp
        }

    def _rad(self, x):
        # Deg 모드면 도->라디안 변환
        return math.radians(x) if self.angle_mode == "Deg" else x

    def _ang(self, x):
        # Deg 모드면 라디안->도 변환
        return math.degrees(x) if self.angle_mode == "Deg" else x

    # ---------- 버튼 동작 ----------
    def on_click(self, t: str):
        try:
            if t == "AC":
                self.display.setText("0")
                return

            if t == "⌫":
                txt = self.display.text()
                self.display.setText("0" if len(txt)<=1 else txt[:-1])
                return

            if t == "+/-":
                self._set_value(-self._get_value())
                return

            if t == "%":
                self._set_value(self._get_value()/100.0)
                return

            # 메모리
            if t == "mc":
                self.memory = 0.0;  return
            if t == "m+":
                self.memory += self._get_value();  return
            if t == "m-":
                self.memory -= self._get_value();  return
            if t == "mr":
                self._set_value(self.memory);  return

            # 각도/라디안 토글 (좌하단 버튼)
            if t == "Deg": # 키는 'Deg'지만 텍스트는 바뀜
                self.angle_mode = "Deg" if self.angle_mode == "Rad" else "Rad"
                self.btn_refs["Deg"].setText(self.angle_mode)
                return

            # 2nd 토글
            if t == "2nd":
                self.is_second = not self.is_second
                self._apply_second_toggle()
                return

            # 숫자/점
            if t.isdigit() or t == ".":
                self._append_digit(t)
                return

            # 괄호/연산자/= 은 표현식으로 처리
            if t in {"(",")","÷","×","−","+","EE"}:
                if t == "EE":  # 지수 표기
                    self.display.setText(self.display.text() + "e")
                else:
                    self.display.setText(self.display.text() + t if self.display.text()!="0" else t)
                return

            if t == "=":
                expr = self._to_python_expr(self.display.text())
                try:
                    val = eval(expr, self._safe_env())
                    self._set_value(val)
                except Exception:
                    self.display.setText("Error")
                return

            # 상수/랜덤
            if t == "π":
                self.display.setText(str(math.pi))
                return
            if t == "e":
                self.display.setText(str(math.e))
                return
            if t == "Rand":
                self._set_value(random.random())
                return

            # 이항: xʸ, ʸ√x  → 기호만 추가
            if t == "xʸ":
                self.display.setText(self.display.text() + "**")
                return
            if t == "ʸ√x":
                # y-th root of x == x**(1/y) → 안내용 형태 삽입
                self.display.setText(f"({self.display.text()})**(1/")  # 뒤에 y 입력 후 ) 하고 =
                return

            # 단항 즉시 계산
            val = self._get_value()
            if t == "x²":
                self._set_value(val**2); return
            if t == "x³":
                self._set_value(val**3); return
            if t == "1/x":
                self._set_value(1.0/val); return
            if t == "²√x":
                self._set_value(math.sqrt(val)); return
            if t == "³√x":
                self._set_value(math.copysign(abs(val)**(1/3), val)); return
            if t == "ln":
                if val<=0: self.display.setText("Error")
                else: self._set_value(math.log(val))
                return
            if t == "log₁₀":
                if val<=0: self.display.setText("Error")
                else: self._set_value(math.log10(val))
                return
            if t == "eˣ":
                self._set_value(math.exp(val)); return
            if t == "10ˣ":
                self._set_value(10**val); return
            if t == "x!":
                if val<0 or float(val)!=int(val): self.display.setText("Error")
                else: self._set_value(math.factorial(int(val)))
                return

            # 삼각/역삼각
            if t in {"sin","cos","tan","sinh","cosh","tanh","sin⁻¹","cos⁻¹","tan⁻¹"}:
                if t == "sin":
                    self._set_value(math.sin(self._rad(val))); return
                if t == "cos":
                    self._set_value(math.cos(self._rad(val))); return
                if t == "tan":
                    # tan 특이점 방지(근사)
                    r = self._rad(val)
                    if abs(math.cos(r)) < 1e-15: self.display.setText("Error")
                    else: self._set_value(math.tan(r))
                    return
                if t == "sinh":
                    self._set_value(math.sinh(val)); return
                if t == "cosh":
                    self._set_value(math.cosh(val)); return
                if t == "tanh":
                    self._set_value(math.tanh(val)); return
                if t == "sin⁻¹":
                    if -1<=val<=1: self._set_value(self._ang(math.asin(val)))
                    else: self.display.setText("Error")
                    return
                if t == "cos⁻¹":
                    if -1<=val<=1: self._set_value(self._ang(math.acos(val)))
                    else: self.display.setText("Error")
                    return
                if t == "tan⁻¹":
                    self._set_value(self._ang(math.atan(val))); return

        except Exception:
            self.display.setText("Error")

    def _append_digit(self, d):
        txt = self.display.text()
        if txt == "0" and d != ".":
            self.display.setText(d)
        else:
            # 소수점 중복 방지(간단 처리)
            if d == ".":
                # 마지막 토큰에 점이 이미 있으면 무시
                last = txt.split()[-1] if " " in txt else txt.split("+-*/()")[-1]
            self.display.setText(txt + d)

    def _apply_second_toggle(self):
        # 토글되는 버튼들 텍스트 교체
        pairs = [
            ("eˣ","ln"),
            ("10ˣ","log₁₀"),
            ("sin","sin⁻¹"),
            ("cos","cos⁻¹"),
            ("tan","tan⁻¹"),
            ("x²","²√x"),
            ("x³","³√x"),
            ("xʸ","ʸ√x"),
        ]
        for a,b in pairs:
            if a in self.btn_refs and b in self.btn_refs:
                # 현재 보이는 것을 반대로
                if self.btn_refs[a].text() == a and self.btn_refs[b].text() == b:
                    # 기본 상태 → 2nd 켜면 좌우 스왑
                    pass
        # 실제 텍스트 교체
        for left,right in pairs:
            if self.is_second:
                if left in self.btn_refs:  self.btn_refs[left].setText(right)
                if right in self.btn_refs: self.btn_refs[right].setText(left)
            else:
                # 기본 라벨로 복구
                if left in self.btn_refs:  self.btn_refs[left].setText(left)
                if right in self.btn_refs: self.btn_refs[right].setText(right)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = IOSCalc()
    w.show()
    sys.exit(app.exec())
