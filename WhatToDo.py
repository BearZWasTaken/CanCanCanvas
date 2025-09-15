from datetime import datetime
from enum import Enum

class WhatToDo:
    class State(Enum):
        UNDONE = 0
        DONE = 1
        IGNORE = 2

    def __init__(self, source="", course_name="", todo_type="", title="", ddl=None, state=State.UNDONE):
        self.source = source
        self.course_name = course_name
        self.todo_type = todo_type
        self.title = title
        self.ddl = ddl
        self.state = state