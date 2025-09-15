import CanvasPuller as cp
import DesktopWidget as dw
from PyQt5.QtCore import QThread
import sys

class CCCManager:
    def __init__(self, api_url, token):
        self.puller = cp.CanvasPuller(api_url, token)
        self.widget = dw.DesktopWidget()

        self.canvas_puller_thread = QThread()
        self.puller.moveToThread(self.canvas_puller_thread)
        self.canvas_puller_thread.started.connect(self.puller.run)
        self.puller.canvas_data_pulled.connect(self.widget.updateCanvasTasks)

        self.canvas_puller_thread.start()
    