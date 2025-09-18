import CanvasPuller as cp
import DesktopWidget as dw
from PyQt5.QtCore import QThread
import sys
import json
import os
import WhatToDo as wtd

SETTINGS_FILE = "configs/settings.json"
WHAT_TO_DO_FILE = "configs/what_to_do.json"
COLORS_FILE = "configs/colors.json"

class CCCManager:
    def __init__(self):
        self.settings = CCCSettings()
        self.colors = {}

        self.what_to_do_list : list[wtd.WhatToDo] = []
        self.sources : list[str] = []

        self.ReadSettings()
        self.ReadTasks()
        self.ReadColors()

        self.puller = cp.CanvasPuller(self)
        self.widget = dw.DesktopWidget(self)

        self.canvas_puller_thread = QThread()
        self.puller.moveToThread(self.canvas_puller_thread)
        self.canvas_puller_thread.started.connect(self.puller.run)
        self.puller.canvas_data_pulled.connect(self.UpdateCanvasTaskList)

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

    def ReadTasks(self):
        if not os.path.exists(WHAT_TO_DO_FILE):
            with open(WHAT_TO_DO_FILE, "w", encoding="utf-8") as f:
                f.write("[]")
        
        with open(WHAT_TO_DO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.what_to_do_list = wtd.InputFromJson(data)
    
    def SaveTasks(self):
        wtd.OutputToJson(WHAT_TO_DO_FILE, self.what_to_do_list)
    
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
        self.puller.Refresh()

    def AddTask(self, task:wtd.WhatToDo):
        if task not in self.what_to_do_list:
            self.what_to_do_list.append(task)

    def DeleteTask(self, task:wtd.WhatToDo):
        if task in self.what_to_do_list:
            self.what_to_do_list.remove(task)

    def UpdateWhatToDoList(self):
        for task in self.what_to_do_list:
            src = task.source
            if src != "Canvas" and src not in self.sources:
                self.sources.append(src)

        self.widget.UpdateModules()
        self.SaveTasks()

    def UpdateCanvasTaskList(self, canvas_tasks:list[wtd.WhatToDo]):
        for task in reversed(self.what_to_do_list):
            if task.source == "Canvas":
                self.DeleteTask(task)
        
        self.what_to_do_list.extend(canvas_tasks)

        self.UpdateWhatToDoList()

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
