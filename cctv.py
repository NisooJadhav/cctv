import sys
import cv2
import winsound
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import *
from PyQt5.QtCore import *

class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        loadUi("cctv.ui", self)
        self.setupUi()

    def setupUi(self):
        self.monitoring.clicked.connect(self.start_monitoring)
        self.volume.clicked.connect(self.set_volume)
        self.exit.clicked.connect(self.close_window)
        self.volumeslider.setVisible(False)
        self.volumeslider.valueChanged.connect(self.set_volume_level)
        self.webcam = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.volume = 500

    def start_monitoring(self):
        print("Monitoring started")
        self.timer.start(10)  # Adjust the interval as needed

    def update_frame(self):
        _, frame = self.webcam.read()
        _, frame2 = self.webcam.read()

        diff = cv2.absdiff(frame, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            if cv2.contourArea(c) < 5000:
                continue
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imwrite("capture.jpg", frame)
            img = QImage("capture.jpg")
            pm = QPixmap.fromImage(img)
            self.capturedwindow.setPixmap(pm)
            winsound.Beep(self.volume, 200)

        self.capturedwindow.setScaledContents(True)
        self.capturedwindow.setPixmap(QPixmap("capture.jpg"))
        self.capturedwindow.setStyleSheet("border-radius: 40px;")
        self.capturedwindow.update()

    def set_volume(self):
        self.volumeslider.setVisible(True)
        print("Volume button clicked")

    def close_window(self):
        self.timer.stop()
        self.webcam.release()
        cv2.destroyAllWindows()
        self.close()

    def set_volume_level(self):
        self.volumelevel.setText(str(self.volumeslider.value() // 10))
        self.volume = self.volumeslider.value() * 10
        cv2.waitKey(2000)
        self.volumeslider.setVisible(False)

def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()