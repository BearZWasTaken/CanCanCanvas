import sys
import CCCManager as cccm
from PyQt5.QtWidgets import QApplication

sys.stdout.reconfigure(encoding="utf-8")

app = QApplication(sys.argv)
cccmanager = cccm.CCCManager()
sys.exit(app.exec_())
