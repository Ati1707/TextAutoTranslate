import sys
import threading
from charset_normalizer import from_bytes
from translators import translate_text

from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QTextEdit, QPushButton,
    QComboBox, QFileDialog, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import QTimer, Qt, Signal, QObject


class TranslationWorker(QObject):
    finished = Signal(str)

    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        translated = translate_text(self.text, translator="google")
        self.finished.emit(translated)


class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.language_combo = None
        self.open_button = None
        self.save_button = None
        self.translation_output = None
        self.text_edit = None
        self.worker = None
        self.setWindowTitle("TextAutoTranslate")
        self.resize(1000, 600)
        self.languages = ["English", "Spanish", "French", "German", "Chinese"]
        self.last_selection = ""
        self.selection_timer = QTimer()
        self.selection_timer.setSingleShot(True)
        self.selection_timer.timeout.connect(self.process_selection)
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Text Editor
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(False)
        self.text_edit.setFontFamily("Courier New")
        self.text_edit.setFontPointSize(12)
        layout.addWidget(self.text_edit, 0, 0, 1, 2)

        # Translation Output
        self.translation_output = QTextEdit()
        self.translation_output.setFontFamily("Courier New")
        self.translation_output.setFontPointSize(12)
        self.translation_output.setReadOnly(True)
        layout.addWidget(self.translation_output, 1, 0, 1, 2)

        # Buttons Layout
        buttons_layout = QHBoxLayout()

        # Open File Button
        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open_file)
        buttons_layout.addWidget(self.open_button)

        # Save File Button
        self.save_button = QPushButton("Save File")
        self.save_button.clicked.connect(self.save_file)
        buttons_layout.addWidget(self.save_button)

        layout.addLayout(buttons_layout, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        # Language Combo Box
        self.language_combo = QComboBox()
        self.language_combo.addItems(self.languages)
        self.language_combo.setCurrentIndex(-1)
        self.language_combo.setPlaceholderText("Select Target Language")
        layout.addWidget(self.language_combo, 2, 1, alignment=Qt.AlignmentFlag.AlignRight)

        # Set row stretch factors
        layout.setRowStretch(0, 7)
        layout.setRowStretch(1, 2)
        layout.setRowStretch(2, 1)

        # Connect selection change handler
        self.text_edit.selectionChanged.connect(self.handle_selection)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            with open(file_path, "rb") as f:
                raw_data = f.read()
                result = from_bytes(raw_data).best()
                encoding = result.encoding if result else 'utf-8'

            try:
                with open(file_path, "r", encoding=encoding) as file:
                    content = file.read()
            except (UnicodeDecodeError, LookupError):
                try:
                    with open(file_path, "r", encoding='utf-16') as file:
                        content = file.read()
                except Exception as e:
                    content = f"Error: Failed to decode file - {str(e)}"

            self.text_edit.setPlainText(content)
            self.text_edit.setFocus()

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            content = self.text_edit.toPlainText()
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def handle_selection(self):
        if self.selection_timer.isActive():
            self.selection_timer.stop()
        self.selection_timer.start(1000)

    def process_selection(self):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText().strip()

        if selected_text and selected_text != self.last_selection:
            self.last_selection = selected_text
            self.start_translation_thread(selected_text)

    def start_translation_thread(self, text):
        self.translation_output.setPlainText("Translating...")

        self.worker = TranslationWorker(text)
        self.thread = threading.Thread(target=self.worker.run)
        self.worker.finished.connect(self.update_translation_output)
        self.thread.start()

    def update_translation_output(self, translated_text):
        self.translation_output.setPlainText(translated_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec())
