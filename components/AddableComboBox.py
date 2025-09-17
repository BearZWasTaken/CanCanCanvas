from PyQt5.QtWidgets import QComboBox, QLineEdit, QStyledItemDelegate, QListView
from PyQt5.QtCore import Qt, pyqtSignal, QSize

class AddableComboBox(QComboBox):
    def __init__(self, options=None):
        super().__init__()
        self.setEditable(False)
        
        if options:
            self.addItems(options)
        
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("⊕ New...")
        self.input_line.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                padding: 2px;
                margin: 2px;
            }
        """)
        self.input_line.returnPressed.connect(self.AddNewOption)
        
        self.setView(QListView())
        self.view().setMinimumWidth(200)
        
    def showPopup(self):
        super().showPopup()
        
        popup = self.view().parentWidget()
        
        new_height = self.view().sizeHintForRow(0) * (self.count() + 1) + 10
        popup.resize(popup.width(), new_height)
        
        self.input_line.setParent(popup)
        self.input_line.setGeometry(
            2,
            self.view().height() + 2,
            popup.width() - 4,
            25
        )
        self.input_line.show()
        self.input_line.setFocus()
        
    def AddNewOption(self):
        new_text = self.input_line.text().strip()
        if new_text and self.findText(new_text) == -1:
            self.addItem(new_text)
            self.setCurrentIndex(self.count() - 1)
        self.input_line.clear()
        self.hidePopup()
