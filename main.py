# main.py
import sys
from PyQt5.QtWidgets import QApplication, QDialog
from gui.file_dialog import FileSelectionDialog
from gui.main_window import VoiceToTextApp

def main():
    app = QApplication(sys.argv)
    
    # Show file selection dialog
    file_dialog = FileSelectionDialog()
    if file_dialog.exec_() == QDialog.Accepted:
        window = VoiceToTextApp(file_dialog.record_file, file_dialog.keywords_file)
        window.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()