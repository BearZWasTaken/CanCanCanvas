from datetime import datetime

class WhatToDo:
    def __init__(self, source="", course_name="", todo_type="", title="", ddl=None):
        self.source = source
        self.course_name = course_name
        self.todo_type = todo_type
        self.title = title
        self.ddl = ddl