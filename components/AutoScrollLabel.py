from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QTimer, Qt

class AutoScrollLabel(QLabel):
    def __init__(self, text="", parent=None, speed=1, pause_time=1000):
        super().__init__(text, parent)
        self.speed = speed
        self.offset = 0
        self.pause_time = pause_time
        self.timer = None
        self.pause_timer = None
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setStyleSheet("background: transparent; padding-left: 8px;")
        self.setMinimumWidth(50)
        self.setMaximumWidth(380)
        self.setText(text)
        self._paused = False

    def setText(self, text):
        super().setText(text)
        self.offset = 0
        self._paused = False
        fm = self.fontMetrics()
        need_scroll = fm.width(text) > self.width() - 8

        # Clean up timers if not needed
        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()
            self.timer = None
        if self.pause_timer:
            self.pause_timer.stop()
            self.pause_timer.deleteLater()
            self.pause_timer = None

        if need_scroll:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.scrollText)
            self.timer.start(30)
            self.pause_timer = QTimer(self)
            self.pause_timer.setSingleShot(True)
            self.pause_timer.timeout.connect(self.resumeScroll)
        self.update()

    def resizeEvent(self, event):
        self.setText(self.text())
        super().resizeEvent(event)

    def scrollText(self):
        if self._paused:
            return
        fm = self.fontMetrics()
        text_width = fm.width(self.text())
        label_width = self.width() - 8
        if text_width <= label_width:
            self.offset = 0
            if self.timer:
                self.timer.stop()
            self.update()
            return
        self.offset += self.speed
        if self.offset > text_width - label_width:
            self.offset = text_width - label_width
            self._paused = True
            if self.timer:
                self.timer.stop()
            if self.pause_timer:
                self.pause_timer.start(self.pause_time)
        self.update()

    def resumeScroll(self):
        self.offset = 0
        self._paused = False
        if self.timer:
            self.timer.start(30)

    def paintEvent(self, event):
        painter = QPainter(self)
        fm = self.fontMetrics()
        text_width = fm.width(self.text())
        label_width = self.width() - 8
        painter.save()
        painter.translate(8, 0)
        if text_width > label_width:
            painter.translate(-self.offset, 0)
        painter.drawText(0, fm.ascent(), self.text())
        painter.restore()