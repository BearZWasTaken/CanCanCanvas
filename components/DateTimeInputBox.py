from PyQt5.QtWidgets import QHBoxLayout, QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt
from datetime import datetime

class DateTimeInputBox(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self.setSpacing(4)

        self.year_input = QLineEdit()
        self.year_input.setMaximumWidth(60)
        self.year_input.setPlaceholderText("YYYY")
        self.addWidget(self.year_input)

        self.year_month_spacing = QLabel("-")
        self.addWidget(self.year_month_spacing)

        self.month_input = QLineEdit()
        self.month_input.setMaximumWidth(45)
        self.month_input.setPlaceholderText("MM")
        self.addWidget(self.month_input)

        self.month_day_spacing = QLabel("-")
        self.addWidget(self.month_day_spacing)

        self.day_input = QLineEdit()
        self.day_input.setMaximumWidth(45)
        self.day_input.setPlaceholderText("DD")
        self.addWidget(self.day_input)

        self.hour_input = QLineEdit()
        self.hour_input.setMaximumWidth(45)
        self.hour_input.setPlaceholderText("HH")
        self.addWidget(self.hour_input)

        self.hour_minute_spacing = QLabel(":")
        self.addWidget(self.hour_minute_spacing)
        
        self.minute_input = QLineEdit()
        self.minute_input.setMaximumWidth(45)
        self.minute_input.setPlaceholderText("mm")
        self.addWidget(self.minute_input)

        self.minute_second_spacing = QLabel(":")
        self.addWidget(self.minute_second_spacing)
        
        self.second_input = QLineEdit()
        self.second_input.setMaximumWidth(45)
        self.second_input.setPlaceholderText("ss")
        self.addWidget(self.second_input)

    def text(self):
        return (
            f"{self.year_input.text().zfill(4)}-"
            f"{self.month_input.text().zfill(2)}-"
            f"{self.day_input.text().zfill(2)}T"
            f"{self.hour_input.text().zfill(2)}:"
            f"{self.minute_input.text().zfill(2)}:"
            f"{self.second_input.text().zfill(2)}"
        )
        
    def to_datetime(self):
        dt = None
        text = self.text()
        if self.text():
            try:
                dt = datetime.fromisoformat(text)
            except ValueError:
                pass
        return dt

    def set_datetime(self, datetime):
        if datetime:
            self.year_input.setText(str(datetime.year))
            self.month_input.setText(f"{datetime.month:02d}")
            self.day_input.setText(f"{datetime.day:02d}")
            
            self.hour_input.setText(f"{datetime.hour:02d}")
            self.minute_input.setText(f"{datetime.minute:02d}")
            self.second_input.setText(f"{datetime.second:02d}")
        else:
            self.year_input.clear()
            self.month_input.clear()
            self.day_input.clear()
            self.hour_input.clear()
            self.minute_input.clear()
            self.second_input.clear()
