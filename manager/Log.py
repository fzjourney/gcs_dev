from PySide6.QtGui import QTextCursor

class Log:
    def log_action(self, message):
        cursor = self.log_text_edit.textCursor()
        cursor.movePosition(QTextCursor.Start)
        
        if cursor.selectedText(): 
            cursor.insertText("\n" + message)
        else:
            cursor.insertText(message) 
        
        self.log_text_edit.setTextCursor(cursor)
        self.log_text_edit.ensureCursorVisible()