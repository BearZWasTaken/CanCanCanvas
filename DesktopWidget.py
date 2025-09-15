from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QSizePolicy, QWidgetItem, QGridLayout
from PyQt5.QtCore import Qt
import ctypes
import WhatToDo as wtd

class DesktopWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.planner_items : dict[wtd.WhatToDo] = {}

        self.SetupModules()

        self.show()

    def SetupModules(self):
        ### Canvas What-To-Do Module
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: rgba(255,255,255,50);")
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0,0,0,0)
        self.grid_layout.setSpacing(10)
        self.grid_widget.setLayout(self.grid_layout)

        self.canvas_scroll = QScrollArea()
        self.canvas_scroll.setWidgetResizable(True)
        self.canvas_scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { width: 8px; background: rgba(0,0,0,50%); }
            QScrollBar::handle:vertical { background: rgba(255,255,255,80%); border-radius: 4px; }
            QScrollBar::add-line, QScrollBar::sub-line { height: 0px; }
        """)
        self.canvas_scroll.viewport().setAttribute(Qt.WA_TranslucentBackground)
        self.canvas_scroll.setWidget(self.grid_widget)
        self.layout.addWidget(self.canvas_scroll)

        # Other Modules
        clock_label1 = QLabel("Block 1")
        clock_label1.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:5px;")
        self.layout.addWidget(clock_label1)

        clock_label2 = QLabel("Block 2")
        clock_label2.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:5px;")
        self.layout.addWidget(clock_label2)

    def UpdateModules(self):
        self.ClearLayout(self.grid_layout)
        
        ### Canvas What-To-Do Module
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Headers
        headers = ["Course", "Title", "DDL"]
        for col, text in enumerate(headers):
            lbl = QLabel(text)
            lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; font-weight:bold;")
            lbl.setAlignment(Qt.AlignLeft)
            self.grid_layout.addWidget(lbl, 0, col)

        # Tasks
        for row, task in enumerate(self.planner_items, start=1):
            course_lbl = QLabel(task.course_name)
            course_lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; border-radius:3px;")
            course_lbl.setAlignment(Qt.AlignLeft)
            self.grid_layout.addWidget(course_lbl, row, 0)

            title_lbl = QLabel(task.title)
            title_lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; border-radius:3px;")
            title_lbl.setAlignment(Qt.AlignLeft)
            self.grid_layout.addWidget(title_lbl, row, 1)

            ddl_text = task.ddl.strftime("%Y-%m-%d %H:%M:%S") if task.ddl else "None"
            ddl_lbl = QLabel(ddl_text)
            ddl_lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; border-radius:3px;")
            ddl_lbl.setAlignment(Qt.AlignLeft)
            self.grid_layout.addWidget(ddl_lbl, row, 2)

    def updateCanvasTasks(self, planner_items):
        self.planner_items = planner_items
        self.UpdateModules()

    def ClearLayout(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.widget():
                widget = item.widget()
                layout.removeWidget(widget)
                widget.setParent(None)
            elif item.layout():
                self.ClearLayout(item.layout())
                layout.removeItem(item)
            else:
                layout.removeItem(item)

