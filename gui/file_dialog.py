from PyQt5.QtWidgets import (QDialog, QPushButton, QVBoxLayout, QWidget, 
                           QHBoxLayout, QLabel, QLineEdit, QFileDialog, QMessageBox)

class FileSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.record_file = ""
        self.keywords_file = ""
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Select Files")
        self.setGeometry(300, 300, 400, 150)
        
        layout = QVBoxLayout()
        
        # Record file selection
        record_layout = QHBoxLayout()
        self.record_path = QLineEdit()
        self.record_path.setReadOnly(True)
        record_btn = QPushButton("Select Record File")
        record_btn.clicked.connect(self.select_record_file)
        record_layout.addWidget(self.record_path)
        record_layout.addWidget(record_btn)
        layout.addWidget(QLabel("Record File:"))
        layout.addLayout(record_layout)
        
        # Keywords file selection
        keywords_layout = QHBoxLayout()
        self.keywords_path = QLineEdit()
        self.keywords_path.setReadOnly(True)
        keywords_btn = QPushButton("Select Keywords File")
        keywords_btn.clicked.connect(self.select_keywords_file)
        keywords_layout.addWidget(self.keywords_path)
        keywords_layout.addWidget(keywords_btn)
        layout.addWidget(QLabel("Keywords File:"))
        layout.addLayout(keywords_layout)
        
        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
        
        self.setLayout(layout)
    
    def select_record_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Record File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file:
            self.record_file = file
            self.record_path.setText(file)
    
    def select_keywords_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Keywords File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file:
            self.keywords_file = file
            self.keywords_path.setText(file)
    
    def accept(self):
        if not self.record_file or not self.keywords_file:
            QMessageBox.warning(self, "Warning", "Please select both files.")
            return
        super().accept()
