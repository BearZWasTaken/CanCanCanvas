import requests
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from datetime import datetime
import WhatToDo as wtd
import time

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
        self.refresh_time = 10
        self.is_refreshing = False
        self.last_refresh = time.time() - self.refresh_time

    def run(self):
        while self.running:
            now = time.time()
            if now - self.last_refresh >= self.refresh_time:
                self.Refresh()
            time.sleep(1)

    def Refresh(self):
        self.is_refreshing = True
        self.GetCourses()
        self.GetPlannerItems()
        self.canvas_data_pulled.emit(self.planner_items)
        self.last_refresh = time.time()
        self.is_refreshing = False

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

        new_planner_items : list[wtd.WhatToDo] = []

        url = f"{self.api_url}/planner/items?per_page=100"
        while url:
            resp = requests.get(url, headers=self.headers)
            
            items = resp.json()
            for item in items:
                course_id = item.get("course_id")
                plannable = item.get("plannable")
                submissions = item.get("submissions")

                state = wtd.WhatToDo.State.UNDONE
                if submissions:
                    if submissions.get('needs_grading'):
                        state = wtd.WhatToDo.State.DONE
                    if submissions.get('graded'):
                        state = wtd.WhatToDo.State.DONE

                course_name = self.courses[course_id] if course_id in self.courses else f"Unknown({course_id})"
                title = plannable['title']
                due_at = plannable.get('due_at')

                ddl = datetime.strptime(due_at, "%Y-%m-%dT%H:%M:%SZ") if due_at else None

                what_to_do = wtd.WhatToDo(source="Canvas", course_name=course_name, title=title, ddl=ddl, state=state)
                new_planner_items.append(what_to_do)

                info = f"{course_name} | {title} | Due: {due_at}"
                print(info)

            url = resp.links.get('next', {}).get('url')
        
        self.planner_items = new_planner_items