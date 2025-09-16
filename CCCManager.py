import CanvasPuller as cp
import DesktopWidget as dw
from PyQt5.QtCore import QThread
import sys
import json
import os
import WhatToDo as wtd

SETTINGS_FILE = "configs/settings.json"
CUSTOM_TASKS_FILE = "configs/custom_tasks.json"
COLORS_FILE = "configs/colors.json"

class CCCManager:
    def __init__(self):
        self.settings = CCCSettings()
        self.colors = {}

        self.custom_tasks : list[wtd.WhatToDo] = []

        self.ReadSettings()
        self.ReadCustomTasks()
        self.ReadColors()

        self.puller = cp.CanvasPuller(self)
        self.widget = dw.DesktopWidget(self)

        self.canvas_puller_thread = QThread()
        self.puller.moveToThread(self.canvas_puller_thread)
        self.canvas_puller_thread.started.connect(self.puller.run)
        self.puller.canvas_data_pulled.connect(self.widget.updateCanvasTasks)

        self.canvas_puller_thread.start()
    
    def ReadSettings(self):
        settings = CCCSettings()

        if not os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                f.write("")

        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            input_settings = json.load(f)
            settings.api_url = input_settings["api_url"] if "api_url" in input_settings else ""
            settings.token = input_settings["token"] if "token" in input_settings else ""
            settings.refresh_time = input_settings["refresh_time"] if "refresh_time" in input_settings else 100

        self.settings = settings
    
    def SaveSettings(self):
        self.settings.OutputToJson(SETTINGS_FILE)

    def ReadCustomTasks(self):
        if not os.path.exists(CUSTOM_TASKS_FILE):
            with open(CUSTOM_TASKS_FILE, "w", encoding="utf-8") as f:
                f.write("[]")
        
        with open(CUSTOM_TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.custom_tasks = wtd.InputFromJson(data)
    
    def SaveCustomTasks(self):
        wtd.OutputToJson(CUSTOM_TASKS_FILE, self.custom_tasks)
    
    def ReadColors(self):
        if not os.path.exists(COLORS_FILE):
            with open(COLORS_FILE, "w", encoding="utf-8") as f:
                f.write("""
                        {
                            \"Canvas\": \"#8B0000\"
                        }
                        """)

        with open(COLORS_FILE, "r", encoding="utf-8") as f:
            self.colors = json.load(f)

    def SaveColors(self):
        with open(COLORS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.colors, f, indent=4, ensure_ascii=False)
    
    def Refresh(self):
        if not self.puller.is_refreshing:
            self.puller.Refresh()

class CCCSettings:
    def __init__(self):
        self.api_url = ""
        self.token = ""
        self.refresh_time = 100

    def OutputToJson(self, filename):
        settings = {
            "api_url": self.api_url,    
            "token": self.token,
            "refresh_time": self.refresh_time
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
