import requests
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import time
from datetime import datetime
import WhatToDo as wtd

class CanvasPuller(QObject):
    canvas_data_pulled = pyqtSignal(list)

    def __init__(self, api_url, token):
        super().__init__()
        self.api_url = api_url
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.courses : dict[int, str] = {}
        self.planner_items : list[wtd.WhatToDo] = []
        self.running = True
        self.refresh_time = 20

    def run(self):
        while self.running:
            self.GetCourses()
            self.GetPlannerItems()
            self.canvas_data_pulled.emit(self.planner_items)
            time.sleep(self.refresh_time)

    def GetCourses(self):
        print("Getting courses data...")

        url = f"{self.api_url}/courses?per_page=100"
        while url:
            resp = requests.get(url, headers=self.headers)
            
            for course in resp.json():
                course_id = course["id"]
                course_name = course["name"]
                self.courses[course_id] = course_name
                print(course_id, course_name)

            url = resp.links.get('next', {}).get('url')

    def GetPlannerItems(self):
        print("Getting planner items data...")
        resp = requests.get(f"{self.api_url}/planner/items", headers=self.headers)

        items = resp.json()

        for item in items:
            course_id = item.get("course_id")
            plannable = item.get("plannable")

            course_name = self.courses[course_id] if course_id in self.courses else f"Unknown({course_id})"
            title = plannable['title']
            due_at = plannable.get('due_at')

            ddl = datetime.strptime(due_at, "%Y-%m-%dT%H:%M:%SZ") if due_at else None
            what_to_do = wtd.WhatToDo(source="Canvas", course_name=course_name, title=title, ddl=ddl)
            self.planner_items.append(what_to_do)

            info = f"{course_name} | {title} | Due: {due_at}"
            print(info)