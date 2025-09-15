import sys
import CCCManager as cccm
from PyQt5.QtWidgets import QApplication
import json
import os

sys.stdout.reconfigure(encoding="utf-8")

settings = {
    "API_URL": "",
    "TOKEN": ""
}

settings_file = "settings.json"
if not os.path.exists(settings_file):
    with open(settings_file, "w", encoding="utf-8") as f:
        f.write("")

with open(settings_file, "r", encoding="utf-8") as f:
    input_settings = json.load(f)
    settings["API_URL"] = input_settings["API_URL"] if "API_URL" in input_settings else ""
    settings["TOKEN"] = input_settings["TOKEN"] if "TOKEN" in input_settings else ""

API_URL = settings["API_URL"]
TOKEN = settings["TOKEN"]

with open(settings_file, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=4, ensure_ascii=False)

app = QApplication(sys.argv)
cccmanager = cccm.CCCManager(API_URL, TOKEN)
sys.exit(app.exec_())
