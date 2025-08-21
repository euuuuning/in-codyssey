import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt

# 웹캠 영상을 처리하고 필터를 적용하는 스레드
class WebcamThread(QThread):
    # 영상 프레임과 필터 적용된 프레임을 시그널로 보냄
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.current_filter = 'none' # 현재 적용된 필터 상태

    def run(self):
        """웹캠을 켜고 프레임을 읽어와 필터를 적용한 후 메인 스레드로 전송"""
        cap = cv2.VideoCapture(0) # 0번 카메라 (기본 웹캠)
        if not cap.isOpened():
            print("오류: 카메라를 열 수 없습니다.")
            return

        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                # 선택된 필터에 따라 이미지 처리
                if self.current_filter == 'grayscale':
                    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2BGR) # UI 표시를 위해 다시 BGR로 변환
                elif self.current_filter == 'sepia':
                    cv_img = self.apply_sepia(cv_img)
                elif self.current_filter == 'cartoon':
                    cv_img = self.apply_cartoon(cv_img)

                # 처리된 이미지를 메인 스레드로 전송
                self.change_pixmap_signal.emit(cv_img)
        
        cap.release() # 스레드 종료 시 카메라 자원 해제

    def stop(self):
        """스레드를 안전하게 종료하기 위한 플래그 설정"""
        self._run_flag = False
        self.wait()

    # --- 필터 적용 메서드 ---
    def apply_sepia(self, img):
        """세피아 필터 적용"""
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        sepia_img = cv2.filter2D(img, -1, kernel)
        # 값 범위를 0-255로 유지
        np.clip(sepia_img, 0, 255, out=sepia_img)
        return sepia_img.astype(np.uint8)

    def apply_cartoon(self, img):
        """만화(카툰) 필터 적용"""
        # 엣지 검출
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        
        # 색상 단순화 (Bilateral Filter)
        color = cv2.bilateralFilter(img, 9, 250, 250)
        
        # 엣지와 색상 이미지를 결합
        cartoon_img = cv2.bitwise_and(color, color, mask=edges)
        return cartoon_img


# 메인 애플리케이션 창
class FilterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("실시간 웹캠 필터 앱")
        self.disply_width = 640
        self.display_height = 480

        # UI 요소 초기화
        self.initUI()

        # 웹캠 스레드 생성 및 시작
        self.thread = WebcamThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def initUI(self):
        """UI 요소들을 생성하고 레이아웃을 설정"""
        # 영상이 표시될 라벨
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        self.image_label.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("웹캠 로딩 중...")

        # 필터 버튼
        btn_original = QPushButton("원본", self)
        btn_grayscale = QPushButton("흑백", self)
        btn_sepia = QPushButton("세피아", self)
        btn_cartoon = QPushButton("만화", self)

        # 버튼 클릭 시그널과 슬롯(메서드) 연결
        btn_original.clicked.connect(lambda: self.set_filter('none'))
        btn_grayscale.clicked.connect(lambda: self.set_filter('grayscale'))
        btn_sepia.clicked.connect(lambda: self.set_filter('sepia'))
        btn_cartoon.clicked.connect(lambda: self.set_filter('cartoon'))
        
        # 버튼들을 담을 수평 레이아웃
        hbox = QHBoxLayout()
        hbox.addWidget(btn_original)
        hbox.addWidget(btn_grayscale)
        hbox.addWidget(btn_sepia)
        hbox.addWidget(btn_cartoon)

        # 전체 화면을 구성할 수직 레이아웃
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def set_filter(self, filter_type):
        """버튼 클릭 시 웹캠 스레드의 필터 종류를 변경"""
        print(f"필터 변경: {filter_type}")
        self.thread.current_filter = filter_type

    def update_image(self, cv_img):
        """웹캠 스레드에서 받은 이미지 프레임을 화면에 업데이트"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """OpenCV 이미지(numpy.ndarray)를 PyQt 이미지(QPixmap)로 변환"""
        # BGR -> RGB 색상 순서 변경
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        # QImage로 변환
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # 화면 크기에 맞게 조절
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def closeEvent(self, event):
        """창이 닫힐 때 웹캠 스레드를 안전하게 종료"""
        self.thread.stop()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    a = FilterApp()
    a.show()
    sys.exit(app.exec_())