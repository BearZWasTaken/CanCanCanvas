from datetime import datetime

class WhatToDo:
    def __init__(self, source="", course_name="", title="", ddl=None):
        self.source = source
        self.course_name = course_name
        self.title = title
        self.ddl = ddl