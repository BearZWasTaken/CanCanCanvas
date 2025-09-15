from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QGridLayout, QPushButton
from PyQt5.QtCore import Qt
import ctypes
import WhatToDo as wtd
import CanvasPuller as cp

class DesktopWidget(QWidget):
    def __init__(self, canvasPuller:cp.CanvasPuller):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.planner_items : list[wtd.WhatToDo] = []

        self.SetupModules()

        self.canvasPuller = canvasPuller

        self.show()

    def SetupModules(self):
        ### Top Bar
        top_bar = QHBoxLayout()
        settings_btn = QPushButton("⚙")
        settings_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(0,0,0,150);
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(50,50,50,200);
            }
        """)
        settings_btn.clicked.connect(self.SettingsBtnClicked)
        top_bar.addWidget(settings_btn, alignment=Qt.AlignLeft)

        refresh_btn = QPushButton("⟲")
        refresh_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(0,0,0,150);
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(50,50,50,200);
            }
        """)
        refresh_btn.clicked.connect(self.RefreshBtnClicked)
        top_bar.addWidget(refresh_btn, alignment=Qt.AlignLeft)

        top_bar.addStretch(1)
        self.layout.addLayout(top_bar)

        ### Canvas What-To-Do Module
        self.canvas_scroll = QScrollArea()
        self.canvas_scroll.setWidgetResizable(True)
        self.canvas_scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { width: 8px; background: rgba(0,0,0,50%); }
            QScrollBar::handle:vertical { background: rgba(255,255,255,80%); border-radius: 4px; }
            QScrollBar::add-line, QScrollBar::sub-line { height: 0px; }
        """)
        self.canvas_scroll.viewport().setAttribute(Qt.WA_TranslucentBackground)
        self.layout.addWidget(self.canvas_scroll)

        # Other Modules
        clock_label1 = QLabel("Block 1")
        clock_label1.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:5px;")
        self.layout.addWidget(clock_label1)

        clock_label2 = QLabel("Block 2")
        clock_label2.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:5px;")
        self.layout.addWidget(clock_label2)

    def UpdateModules(self):
        ### Canvas What-To-Do Module
        grid_widget = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0,0,0,0)
        grid_layout.setSpacing(4)
        grid_widget.setLayout(grid_layout)
        grid_widget.setStyleSheet("background: rgba(255,255,255,50);")

        # Headers
        headers = ["Course", "Title", "DDL", ":)"]
        for col, text in enumerate(headers):
            lbl = QLabel(text)
            lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; font-weight:bold;")
            lbl.setAlignment(Qt.AlignLeft)
            grid_layout.addWidget(lbl, 0, col)

        # Tasks
        for row, task in enumerate(self.planner_items, start=1):
            course_lbl = QLabel(task.course_name)
            course_lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; border-radius:3px;")
            course_lbl.setAlignment(Qt.AlignLeft)
            grid_layout.addWidget(course_lbl, row, 0)

            title_lbl = QLabel(task.title)
            title_lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; border-radius:3px;")
            title_lbl.setAlignment(Qt.AlignLeft)
            grid_layout.addWidget(title_lbl, row, 1)

            ddl_text = task.ddl.strftime("%Y-%m-%d %H:%M:%S") if task.ddl else "None"
            ddl_lbl = QLabel(ddl_text)
            ddl_lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; border-radius:3px;")
            ddl_lbl.setAlignment(Qt.AlignLeft)
            grid_layout.addWidget(ddl_lbl, row, 2)

            state_text = "　" if task.state == wtd.WhatToDo.State.UNDONE \
                    else "√" if task.state == wtd.WhatToDo.State.DONE \
                    else "—" if task.state == wtd.WhatToDo.State.IGNORE \
                    else "？"
            state_lbl = QLabel(state_text)
            state_lbl.setFixedWidth(39)
            state_lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; border-radius:3px; font-weight:bold;")
            state_lbl.setAlignment(Qt.AlignCenter)
            grid_layout.addWidget(state_lbl, row, 3)
        
        old_widget = self.canvas_scroll.takeWidget()
        if old_widget:
            old_widget.deleteLater()
        self.canvas_scroll.setWidget(grid_widget)

    def updateCanvasTasks(self, planner_items):
        self.planner_items = planner_items
        self.UpdateModules()

    def SettingsBtnClicked(self):
        print('ok')

    def RefreshBtnClicked(self):
        if not self.canvasPuller.is_refreshing:
            self.canvasPuller.Refresh()
