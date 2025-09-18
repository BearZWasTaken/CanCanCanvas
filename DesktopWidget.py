from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QGridLayout, QPushButton, \
                            QLineEdit, QMenu, QWidgetAction, QFormLayout, \
                            QDialog, QColorDialog, QDialogButtonBox
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
import WhatToDo as wtd
from components import AutoScrollLabel as asl, DateTimeInputBox as dtib, AddableComboBox as acb
from datetime import datetime

class DesktopWidget(QWidget):
    def __init__(self, cccmanager):
        super().__init__()

        self.cccmanager = cccmanager

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.planner_items = cccmanager.what_to_do_list
        self.sources = cccmanager.sources

        self.source_colors = cccmanager.colors

        self.SetupModules()

        self.filterFunc = None
        self.sortFunc = None

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

        # Color
        self.color_btn = QPushButton("☀")
        self.color_btn.setStyleSheet("""
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
        top_bar.addWidget(self.color_btn, alignment=Qt.AlignLeft)
        self.color_btn.mousePressEvent = self.ColorBtnClicked

        # Add
        self.add_btn = QPushButton("＋")
        self.add_btn.setStyleSheet("""
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
        top_bar.addWidget(self.add_btn, alignment=Qt.AlignLeft)
        self.add_btn.mousePressEvent = self.AddBtnClicked

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
        chart_title = QLabel("What-To-Do?")
        chart_title.setStyleSheet("color:white; background-color: rgba(0,0,0,150); padding:6px; font-size:18px; font-weight:bold; border-radius:6px;")
        chart_title.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(chart_title)

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

        # Apply filterFunc if set
        if self.filterFunc:
            shown_tasks = list(filter(self.filterFunc, self.planner_items))
        else:
            shown_tasks = self.planner_items
        
        # Apply sortFunc if set
        if self.sortFunc:
            shown_tasks.sort(key=self.sortFunc)
        else:
            shown_tasks.sort(key=SortByDDL)

        # Tasks
        for row, task in enumerate(shown_tasks, start=1):
            bkgrd_color = self.source_colors.get(task.source, "#000000")
            bkgrd_rgba = hex_with_alpha(bkgrd_color, 150)

            course_lbl = asl.AutoScrollLabel(task.course_name)
            course_lbl.setStyleSheet(f"color:white; background-color: {bkgrd_rgba}; padding:3px; border-radius:3px;")
            course_lbl.setAlignment(Qt.AlignLeft)
            course_lbl.setMaximumWidth(max_widths[0])
            grid_layout.addWidget(course_lbl, row, 0)

            title_lbl = asl.AutoScrollLabel(task.title)
            title_lbl.setStyleSheet(f"color:white; background-color: {bkgrd_rgba}; padding:3px; border-radius:3px;")
            title_lbl.setAlignment(Qt.AlignLeft)
            title_lbl.setMaximumWidth(max_widths[1])
            title_lbl.mouseDoubleClickEvent = lambda event, t=task: self.EditTaskDialog(t)
            grid_layout.addWidget(title_lbl, row, 1)

            ddl_text = task.ddl.strftime("%Y-%m-%d %H:%M:%S") if task.ddl else "None"
            ddl_lbl = asl.AutoScrollLabel(ddl_text)
            ddl_lbl.setStyleSheet(f"color:white; background-color: {bkgrd_rgba}; padding:3px; border-radius:3px;")
            ddl_lbl.setAlignment(Qt.AlignLeft)
            ddl_lbl.setMaximumWidth(max_widths[2])
            grid_layout.addWidget(ddl_lbl, row, 2)

            state_text = "　" if task.state == wtd.WhatToDo.State.UNDONE \
                    else "√" if task.state == wtd.WhatToDo.State.DONE \
                    else "—" if task.state == wtd.WhatToDo.State.IGNORE \
                    else "？"
            state_lbl = QLabel(state_text)
            state_lbl.setFixedWidth(39)
            state_lbl.setStyleSheet(f"color:white; background-color: {bkgrd_rgba}; padding:3px; border-radius:3px; font-weight:bold;")
            state_lbl.setAlignment(Qt.AlignCenter)
            grid_layout.addWidget(state_lbl, row, 3)
        
        chart_layout = QVBoxLayout()
        chart_layout.setContentsMargins(0,0,0,0)
        chart_layout.setSpacing(8)
        chart_layout.addWidget(grid_widget)

        chart_container_widget = QWidget()
        chart_container_widget.setStyleSheet("background: transparent;")
        chart_container_widget.setLayout(chart_layout)

        old_widget = self.canvas_scroll.takeWidget()
        if old_widget:
            old_widget.deleteLater()
        self.canvas_scroll.setWidget(chart_container_widget)

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

    def RefreshBtnClicked(self):
        self.cccmanager.Refresh()

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

    def ColorBtnClicked(self, event):
        menu = QMenu(self)
        action_widget = QWidgetAction(menu)
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        widget.setLayout(layout)

        def handle_color_pick(src, btn):
            color = QColorDialog.getColor(parent=self)
            if color.isValid():
                self.source_colors[src] = color.name()
                btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 12px;")
                self.cccmanager.SaveColors()
                self.UpdateModules()

        for src in self.sources:
            row = QHBoxLayout()
            label = QLabel(src)
            color_btn = QPushButton()
            color_btn.setFixedSize(24, 24)
            color_btn.setStyleSheet(f"background-color: {self.source_colors.get(src, '#444444')}; border-radius: 12px;")
            color_btn.clicked.connect(lambda checked=False, src=src, btn=color_btn: handle_color_pick(src, btn))
            row.addWidget(label)
            row.addWidget(color_btn)
            layout.addLayout(row)

        action_widget.setDefaultWidget(widget)
        menu.addAction(action_widget)
        menu.exec_(self.color_btn.mapToGlobal(self.color_btn.rect().bottomLeft()))

    def AddBtnClicked(self, event):
        menu = QMenu(self)
        action_widget = QWidgetAction(menu)
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        widget.setLayout(layout)
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)
        layout.addLayout(form_layout)

        title_input = QLineEdit()
        form_layout.addRow("Title:", title_input)

        course_input = QLineEdit()
        form_layout.addRow("Course:", course_input)

        ddl_input = dtib.DateTimeInputBox()
        form_layout.addRow("DDL:", ddl_input)

        source_input = acb.AddableComboBox(self.sources)
        form_layout.addRow("Source:", source_input)

        type_input = QLineEdit()
        form_layout.addRow("Type:", type_input)

        add_btn = QPushButton("Add")

        def AddTask():
            title = title_input.text().strip()
            course = course_input.text().strip()
            source = source_input.currentText().strip()
            todo_type = type_input.text().strip()
            if not title:
                return
            
            ddl = ddl_input.to_datetime()

            new_task = wtd.WhatToDo(source=source, course_name=course, todo_type=todo_type, title=title, ddl=ddl, state=wtd.WhatToDo.State.UNDONE)
            self.cccmanager.AddTask(new_task)
            self.cccmanager.SaveTasks()
            self.cccmanager.AddTask(source)

            self.UpdateModules()
            menu.close()

        add_btn.clicked.connect(AddTask)
        layout.addWidget(add_btn)
        action_widget.setDefaultWidget(widget)
        menu.addAction(action_widget)
        menu.exec_(self.add_btn.mapToGlobal(self.add_btn.rect().bottomLeft()))
    
    def EditTaskDialog(self, task):
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Set best position to show
        cursor_pos = QCursor.pos()
        dialog.move(cursor_pos.x() + 20, cursor_pos.y())

        dialog.setWindowTitle("Edit Task")
        dialog.setStyleSheet("""
            QDialog {
                background: rgba(50, 50, 50, 150);
                border-radius: 5px;
            }
            QLabel {
                color: white;
            }
            QLineEdit, QComboBox {
                background: rgba(255, 255, 255, 200);
                border: 1px solid gray;
                border-radius: 3px;
                padding: 3px;
            }
        """)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        title_input = QLineEdit(task.title)
        form_layout.addRow("Title:", title_input)
        
        course_input = QLineEdit(task.course_name)
        form_layout.addRow("Course:", course_input)
        
        ddl_input = dtib.DateTimeInputBox()
        if task.ddl:
            ddl_input.set_datetime(task.ddl)
        form_layout.addRow("DDL:", ddl_input)
        
        source_input = acb.AddableComboBox(self.sources)
        source_input.setCurrentText(task.source)
        form_layout.addRow("Source:", source_input)
        
        type_input = QLineEdit(task.todo_type)
        form_layout.addRow("Type:", type_input)
        
        state_combo = acb.AddableComboBox(["UNDONE", "√", "—", "(delete)"], addable=False)
        state_combo.setCurrentText(task.state.name)
        form_layout.addRow("State:", state_combo)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog_result = dialog.exec_()

        if dialog_result == QDialog.Accepted:
            task.title = title_input.text().strip()
            task.course_name = course_input.text().strip()
            task.ddl = ddl_input.to_datetime()
            task.source = source_input.currentText().strip()
            task.todo_type = type_input.text().strip()
            
            new_state = state_combo.currentText()
            if new_state == "UNDONE":
                task.state = wtd.WhatToDo.State.UNDONE
            elif new_state == "√":
                task.state = wtd.WhatToDo.State.DONE
            elif new_state == "—":
                task.state = wtd.WhatToDo.State.IGNORE
            elif new_state == "(delete)":
                self.cccmanager.DeleteTask(task)
            
            self.cccmanager.UpdateWhatToDoList()

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

def hex_with_alpha(hex_color, alpha):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"

def SortByDDL(task):
    ddl_value = task.ddl if task.ddl else datetime.max
    return ddl_value
