from PySide6.QtGui import QTextCursor

class Log:
    def __init__(self, log_text_edit):
        self.log_text_edit = log_text_edit  

    def log_callback(self, message):
        cursor = self.log_text_edit.textCursor()
        cursor.movePosition(QTextCursor.Start) 
        cursor.insertText("\n" + message) 
        self.log_text_edit.setTextCursor(cursor)
        self.log_text_edit.ensureCursorVisible()