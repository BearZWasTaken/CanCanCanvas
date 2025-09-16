from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QGridLayout, QPushButton
from PyQt5.QtWidgets import QLineEdit, QMenu, QWidgetAction, QApplication, QFormLayout
from PyQt5.QtCore import Qt
import ctypes
import WhatToDo as wtd
import CanvasPuller as cp
import AutoScrollLabel as asl

class DesktopWidget(QWidget):
    def __init__(self, cccmanager):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.planner_items : list[wtd.WhatToDo] = []

        self.SetupModules()

        self.cccmanager = cccmanager
        self.canvasPuller = cccmanager.puller

        self.filterFunc = None

        self.show()

    def SetupModules(self):
        ### Top Bar
        # Settings
        top_bar = QHBoxLayout()
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setStyleSheet("""
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
        self.settings_btn.clicked.connect(self.SettingsBtnClicked)
        top_bar.addWidget(self.settings_btn, alignment=Qt.AlignLeft)

        self.api_url_input = QLineEdit()
        self.token_input = QLineEdit()
        self.refresh_time_input = QLineEdit()
        
        # Refresh
        self.refresh_btn = QPushButton("⟲")
        self.refresh_btn.setStyleSheet("""
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
        self.refresh_btn.clicked.connect(self.RefreshBtnClicked)
        top_bar.addWidget(self.refresh_btn, alignment=Qt.AlignLeft)

        # Filter
        self.filter_btn = QPushButton("☆")
        self.filter_btn.setStyleSheet("""
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
        top_bar.addWidget(self.filter_btn, alignment=Qt.AlignLeft)
        self.filter_btn.mousePressEvent = self.FilterBtnClicked

        top_bar.addStretch(1)

        # Drag
        self.drag_btn = QPushButton("✥")
        self.drag_btn.setStyleSheet("""
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
        self.drag_btn.setCursor(Qt.OpenHandCursor)
        top_bar.addWidget(self.drag_btn, alignment=Qt.AlignRight)

        self.drag_btn.installEventFilter(self)
        self._drag_active = False
        self._drag_pos = None

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

        max_widths = [140, 380, 190, 40]

        # Headers
        headers = ["Course", "Title", "DDL", ":)"]
        for col, text in enumerate(headers):
            lbl = QLabel(text)
            lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; font-weight:bold;")
            lbl.setAlignment(Qt.AlignLeft)
            lbl.setMaximumWidth(max_widths[col])
            grid_layout.addWidget(lbl, 0, col)

        # Apply filterFunc if set, otherwise show all
        if self.filterFunc:
            shown_tasks = list(filter(self.filterFunc, self.planner_items))
        else:
            shown_tasks = self.planner_items

        # Tasks
        for row, task in enumerate(shown_tasks, start=1):
            course_lbl = asl.AutoScrollLabel(task.course_name)
            course_lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; border-radius:3px;")
            course_lbl.setAlignment(Qt.AlignLeft)
            course_lbl.setMaximumWidth(max_widths[0])
            grid_layout.addWidget(course_lbl, row, 0)

            title_lbl = asl.AutoScrollLabel(task.title)
            title_lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; border-radius:3px;")
            title_lbl.setAlignment(Qt.AlignLeft)
            title_lbl.setMaximumWidth(max_widths[1])
            grid_layout.addWidget(title_lbl, row, 1)

            ddl_text = task.ddl.strftime("%Y-%m-%d %H:%M:%S") if task.ddl else "None"
            ddl_lbl = asl.AutoScrollLabel(ddl_text)
            ddl_lbl.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:3px; border-radius:3px;")
            ddl_lbl.setAlignment(Qt.AlignLeft)
            ddl_lbl.setMaximumWidth(max_widths[2])
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
        menu = QMenu(self)

        action_widget = QWidgetAction(menu)
        widget = QWidget()
        widget_layout = QVBoxLayout()
        widget_layout.setContentsMargins(5,5,5,5)
        widget.setLayout(widget_layout)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)

        self.api_url_input.setPlaceholderText("API URL")
        self.api_url_input.setText(self.cccmanager.settings.api_url)
        form_layout.addRow("API URL:", self.api_url_input)

        self.token_input.setPlaceholderText("Token")
        self.token_input.setText(self.cccmanager.settings.token)
        form_layout.addRow("Token:", self.token_input)

        self.refresh_time_input.setPlaceholderText("Refresh time")
        self.refresh_time_input.setText(str(self.cccmanager.settings.refresh_time))
        form_layout.addRow("Refresh time:", self.refresh_time_input)

        widget_layout.addLayout(form_layout)

        save_btn = QPushButton("Save")
        
        def Save():
            self.cccmanager.settings.api_url = self.api_url_input.text()
            self.cccmanager.settings.token = self.token_input.text()
            try:
                rt = int(self.refresh_time_input.text())
                if rt < 10: rt = 10
                self.cccmanager.settings.refresh_time = rt
            except ValueError:
                pass
            self.cccmanager.SaveSettings()
            menu.close()
        
        save_btn.clicked.connect(Save)
        widget_layout.addWidget(save_btn)

        action_widget.setDefaultWidget(widget)
        menu.addAction(action_widget)

        menu.exec_(self.settings_btn.mapToGlobal(self.settings_btn.rect().bottomLeft()))

    def FilterBtnClicked(self, event):
        if event.button() == Qt.LeftButton:
            if self.filterFunc is None:
                self.filterFunc = lambda task: task.state == wtd.WhatToDo.State.UNDONE
                self.filter_btn.setText("★")
            else:
                self.filterFunc = None
                self.filter_btn.setText("☆")
            self.UpdateModules()
        
        elif event.button() == Qt.RightButton:
            menu = QMenu(self)
            action_widget = QWidgetAction(menu)
            widget = QWidget()
            layout = QVBoxLayout()
            layout.setContentsMargins(5,5,5,5)
            widget.setLayout(layout)

            from PyQt5.QtWidgets import QCheckBox

            switch1 = QCheckBox("Enable feature A")
            switch2 = QCheckBox("Enable feature B")
            switch3 = QCheckBox("Enable feature C")
            layout.addWidget(switch1)
            layout.addWidget(switch2)
            layout.addWidget(switch3)

            action_widget.setDefaultWidget(widget)
            menu.addAction(action_widget)
            menu.exec_(self.filter_btn.mapToGlobal(self.filter_btn.rect().bottomLeft()))

    def RefreshBtnClicked(self):
        if not self.canvasPuller.is_refreshing:
            self.canvasPuller.Refresh()

    def eventFilter(self, source, event):
        if source == self.drag_btn:
            if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
                self._drag_active = True
                self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                self.drag_btn.setCursor(Qt.ClosedHandCursor)
                return True
            elif event.type() == event.MouseMove and self._drag_active:
                self.move(event.globalPos() - self._drag_pos)
                return True
            elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
                self._drag_active = False
                self.drag_btn.setCursor(Qt.OpenHandCursor)
                return True
        return super().eventFilter(source, event)
