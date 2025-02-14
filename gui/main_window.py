# gui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QTextEdit, QVBoxLayout, 
                           QWidget, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                           QFileDialog, QMessageBox, QDialog)
from utils.file_handler import FileHandler
from utils.voice_recorder import VoiceRecorderThread
from gui.file_dialog import FileSelectionDialog

class VoiceToTextApp(QMainWindow):
    def __init__(self, record_file, keywords_file):
        super().__init__()
        self.record_file = record_file
        self.keywords_file = keywords_file
        self.file_handler = FileHandler(record_file, keywords_file)
        
        self.setWindowTitle("Voice to Text with Keyword Filter")
        self.setGeometry(100, 100, 800, 500)
        
        self.keywords = self.file_handler.load_keywords()
        self.recorded_logs = self.file_handler.load_recorded()
        
        self.initUI()
        self.recorder_thread = None
        
        # Display existing records in the recorded area
        for record in self.recorded_logs:
            self.recorded_area.append(f"[{record['timestamp']}] {record['text']}")

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()

        # File paths display
        files_layout = QHBoxLayout()
        files_layout.addWidget(QLabel(f"Record File: {self.record_file}"))
        files_layout.addWidget(QLabel(f"Keywords File: {self.keywords_file}"))
        main_layout.addLayout(files_layout)

        panel_layout = QHBoxLayout()
        
        log_panel = QVBoxLayout()
        log_panel.addWidget(QLabel("Log"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        log_panel.addWidget(self.log_area)
        panel_layout.addLayout(log_panel)

        recorded_panel = QVBoxLayout()
        recorded_panel.addWidget(QLabel("Record"))
        self.recorded_area = QTextEdit()
        self.recorded_area.setReadOnly(True)
        recorded_panel.addWidget(self.recorded_area)
        panel_layout.addLayout(recorded_panel)

        keyword_layout = QVBoxLayout()
        keyword_layout.addWidget(QLabel("Library Keywords"))
        self.keyword_list = QListWidget()
        self.keyword_list.addItems(self.keywords)
        keyword_layout.addWidget(self.keyword_list)

        self.keyword_input = QLineEdit()
        keyword_layout.addWidget(self.keyword_input)

        add_btn = QPushButton("Add Keyword")
        add_btn.clicked.connect(self.add_keyword)
        keyword_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove Keyword")
        remove_btn.clicked.connect(self.remove_keyword)
        keyword_layout.addWidget(remove_btn)

        # Import and Export buttons
        import_export_layout = QHBoxLayout()
        
        import_btn = QPushButton("Import Record")
        import_btn.clicked.connect(self.import_recorded)
        import_export_layout.addWidget(import_btn)

        export_btn = QPushButton("Export Record")
        export_btn.clicked.connect(self.export_recorded)
        import_export_layout.addWidget(export_btn)
        
        keyword_layout.addLayout(import_export_layout)

        panel_layout.addLayout(keyword_layout)
        main_layout.addLayout(panel_layout)

        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Mulai Rekam")
        self.start_button.clicked.connect(self.start_recording)
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Rekam")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        # Add Return to File Selection button
        return_btn = QPushButton("Change Files")
        return_btn.clicked.connect(self.return_to_file_selection)
        control_layout.addWidget(return_btn)
        
        main_layout.addLayout(control_layout)
        main_widget.setLayout(main_layout)

    def return_to_file_selection(self):
        # Stop recording if active
        if self.recorder_thread:
            self.stop_recording()
        
        # Save current data
        self.file_handler.save_recorded(self.recorded_logs)
        self.file_handler.save_keywords(self.keywords)
        
        # Show file selection dialog
        file_dialog = FileSelectionDialog()
        if file_dialog.exec_() == QDialog.Accepted:
            # Update file paths
            self.record_file = file_dialog.record_file
            self.keywords_file = file_dialog.keywords_file
            self.file_handler = FileHandler(self.record_file, self.keywords_file)
            
            # Clear and reload data
            self.recorded_area.clear()
            self.keyword_list.clear()
            
            # Load new data
            self.keywords = self.file_handler.load_keywords()
            self.recorded_logs = self.file_handler.load_recorded()
            
            # Update UI
            self.keyword_list.addItems(self.keywords)
            for record in self.recorded_logs:
                self.recorded_area.append(f"[{record['timestamp']}] {record['text']}")
            
            # Update file paths in UI
            self.centralWidget().layout().itemAt(0).layout().itemAt(0).widget().setText(f"Record File: {self.record_file}")
            self.centralWidget().layout().itemAt(0).layout().itemAt(1).widget().setText(f"Keywords File: {self.keywords_file}")

    def start_recording(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.recorder_thread = VoiceRecorderThread(self.keywords)
        self.recorder_thread.textUpdated.connect(self.update_log)
        self.recorder_thread.recordedUpdated.connect(self.update_recorded)
        self.recorder_thread.start()

    def stop_recording(self):
        if self.recorder_thread:
            self.recorder_thread.stop()
            self.recorder_thread.wait()
            self.recorder_thread = None
            
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_log(self, timestamp, text):
        formatted_text = f"[{timestamp}] {text}"
        self.log_area.append(formatted_text)

    def update_recorded(self, timestamp, text):
        self.recorded_logs.append({'timestamp': timestamp, 'text': text})
        formatted_text = f"[{timestamp}] {text}"
        self.recorded_area.append(formatted_text)
        # Auto-save to file when new record is added
        self.file_handler.save_recorded(self.recorded_logs)

    def add_keyword(self):
        keyword = self.keyword_input.text().strip()
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.keyword_list.addItem(keyword)
            self.file_handler.save_keywords(self.keywords)
        self.keyword_input.clear()

    def remove_keyword(self):
        selected_item = self.keyword_list.currentItem()
        if selected_item:
            self.keywords.remove(selected_item.text())
            self.keyword_list.takeItem(self.keyword_list.row(selected_item))
            self.file_handler.save_keywords(self.keywords)

    def import_recorded(self):
        try:
            filepath, _ = QFileDialog.getOpenFileName(
                self, "Import Records", "", "CSV Files (*.csv);;All Files (*)"
            )
            if filepath:
                with open(filepath, 'r') as file:
                    import_handler = FileHandler(filepath, self.keywords_file)
                    imported_records = import_handler.load_recorded()
                    
                    if imported_records:
                        self.recorded_area.clear()
                        self.recorded_logs.extend(imported_records)
                        for record in self.recorded_logs:
                            formatted_text = f"[{record['timestamp']}] {record['text']}"
                            self.recorded_area.append(formatted_text)
                        self.file_handler.save_recorded(self.recorded_logs)
                        QMessageBox.information(self, "Success", "Records imported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def export_recorded(self):
        try:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Export Records", "", "CSV Files (*.csv);;All Files (*)"
            )
            if filepath:
                export_handler = FileHandler(filepath, self.keywords_file)
                export_handler.save_recorded(self.recorded_logs)
                QMessageBox.information(self, "Success", "Records exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting records: {str(e)}")

    def closeEvent(self, event):
        self.stop_recording()
        self.file_handler.save_recorded(self.recorded_logs)
        self.file_handler.save_keywords(self.keywords)
        event.accept()