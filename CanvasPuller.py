import requests
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime
import WhatToDo as wtd
import time
import threading

class CanvasPuller(QObject):
    canvas_data_pulled = pyqtSignal(list)

    def __init__(self, cccmanager):
        super().__init__()
        self.cccmanager = cccmanager

        self.headers = {"Authorization": f"Bearer {self.cccmanager.settings.token}"}
        self.courses : dict[int, str] = {}
        self.planner_items : list[wtd.WhatToDo] = []

        self.running = True
        self.refresh_lock = threading.Lock()
        self.last_refresh = time.time() - self.cccmanager.settings.refresh_time

    def run(self):
        while self.running:
            now = time.time()
            if now - self.last_refresh >= self.cccmanager.settings.refresh_time:
                self.Refresh()
            time.sleep(1)

    def Refresh(self):
        if not self.refresh_lock.acquire(blocking=False):
            print("Refresh skipped (already refreshing)")
            return

        def refresh_worker():
            try:
                self.GetCourses()
                self.GetPlannerItems()
                self.canvas_data_pulled.emit(self.planner_items)
                self.last_refresh = time.time()
                print("Refresh finished")
            finally:
                self.refresh_lock.release()

        threading.Thread(target=refresh_worker, daemon=True).start()

    def GetCourses(self):
        print("Getting courses data...")

        url = f"{self.cccmanager.settings.api_url}/courses?per_page=100"
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

        url = f"{self.cccmanager.settings.api_url}/planner/items?per_page=100"
        while url:
            resp = requests.get(url, headers=self.headers)
            
            items = resp.json()
            for item in items:
                course_id = item.get("course_id")
                plannable = item.get("plannable")
                submissions = item.get("submissions")
                description = item.get('description')

                state = wtd.WhatToDo.State.UNDONE
                if submissions:
                    if submissions.get('needs_grading'):
                        state = wtd.WhatToDo.State.DONE
                    if submissions.get('graded'):
                        state = wtd.WhatToDo.State.DONE

                course_name = self.courses[course_id] if course_id in self.courses else f"Unknown({course_id})"
                title = plannable.get('title')
                due_at = plannable.get('due_at')

                ddl = datetime.strptime(due_at, "%Y-%m-%dT%H:%M:%SZ") if due_at else None

                what_to_do = wtd.WhatToDo(source="Canvas", course_name=course_name, title=title,
                                          description=description, ddl=ddl, state=state)
                new_planner_items.append(what_to_do)

                info = f"{course_name} | {title} | Due: {due_at}"
                print(info)

            url = resp.links.get('next', {}).get('url')
        
        self.planner_items = new_planner_items