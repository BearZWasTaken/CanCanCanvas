from datetime import datetime
from enum import Enum
import json

class WhatToDo:
    class State(Enum):
        UNDONE = 0
        DONE = 1
        IGNORE = 2

    def __init__(self, source="", course_name="", todo_type="", title="", ddl=None, state=State.UNDONE, \
                 dict=None):
        if dict is None:
            self.source = source
            self.course_name = course_name
            self.todo_type = todo_type
            self.title = title
            self.ddl = ddl
            self.state = state
        else:
            self.source = dict.get("source", "")
            self.course_name = dict.get("course_name", "")
            self.todo_type = dict.get("todo_type", "")
            self.title = dict.get("title", "")
            ddl_str = dict.get("ddl", None)
            self.ddl = datetime.fromisoformat(ddl_str) if ddl_str else None
            state_value = dict.get("state", 0)
            self.state = WhatToDo.State(state_value) if state_value in [e.value for e in WhatToDo.State] else WhatToDo.State.UNDONE

    def ToDict(self):
        return {
            "source": self.source,
            "course_name": self.course_name,
            "todo_type": self.todo_type,
            "title": self.title,
            "ddl": self.ddl.isoformat() if self.ddl else None,
            "state": self.state.value
        }

def InputFromJson(data):
    tasks = []
    for item in data:
        task = WhatToDo(dict=item)
        tasks.append(task)
    return tasks

def OutputToJson(file_path, tasks):
    with open(file_path, "w", encoding="utf-8") as f:
        tasks_list = [task.ToDict() for task in tasks]
        json.dump(tasks_list, f, indent=4, ensure_ascii=False)
