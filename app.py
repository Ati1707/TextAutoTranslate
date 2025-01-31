import threading
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QTextEdit, QPushButton,
    QComboBox, QFileDialog, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import QTimer, Qt
from charset_normalizer import from_bytes
from translation_worker import TranslationWorker

TRANSLATION_PROVIDERS = {
    "Google", "KoboldCPP"
}


class TranslatorApp(QWidget):

    def __init__(self, llm_url):
        super().__init__()
        self.llm_url = llm_url
        self.thread = None
        self.current_file_path = None
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
        self.translator_combo = None
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

        # Translator Selection Combo Box
        self.translator_combo = QComboBox()
        self.translator_combo.addItems(list(TRANSLATION_PROVIDERS))
        self.translator_combo.setCurrentIndex(0)

        # Combine buttons and translator combo in a horizontal layout
        left_header_layout = QHBoxLayout()
        left_header_layout.addLayout(buttons_layout)
        left_header_layout.addWidget(self.translator_combo)
        left_header_layout.addStretch()  # Push elements to the left

        # Add combined layout to grid
        layout.addLayout(left_header_layout, 2, 0)

        # Language Combo Box
        self.language_combo = QComboBox()
        self.language_combo.addItems(self.languages)
        self.language_combo.setCurrentIndex(-1)
        self.language_combo.setPlaceholderText("Select Target Language")
        layout.addWidget(self.language_combo, 2, 1, alignment=Qt.AlignmentFlag.AlignRight)

        # Update language combo label when translator changes
        self.translator_combo.currentTextChanged.connect(self.update_language_combo_label)

        # Set row stretch factors
        layout.setRowStretch(0, 7)
        layout.setRowStretch(1, 2)
        layout.setRowStretch(2, 1)

        # Connect selection change handler
        self.text_edit.selectionChanged.connect(self.handle_selection)

    def update_window_title(self):
        """Update window title with current file path if available"""
        if self.current_file_path:
            self.setWindowTitle(f"TextAutoTranslate - {self.current_file_path}")
        else:
            self.setWindowTitle("TextAutoTranslate")

    def update_language_combo_label(self, translator):
        if translator == "LLM":
            self.language_combo.setPlaceholderText("Select Source Language")
        else:
            self.language_combo.setPlaceholderText("Select Target Language")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*)"
        )

        if file_path:
            self.current_file_path = file_path
            self.update_window_title()
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
        if self.current_file_path:
            # Overwrite existing file
            content = self.text_edit.toPlainText()
            try:
                reply = QMessageBox.question(self, "Confirm File Overwrite",
                                             f"You are about to overwrite:{self.current_file_path}"
                                             f"This will permanently replace the existing file. Are you sure you want to continue?",
                                             QMessageBox.StandardButton.Yes,
                                             QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    with open(self.current_file_path, "w", encoding="utf-8") as file:
                        file.write(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
        else:
            # Save as new file
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                "",
                "All Files (*)"
            )
            if file_path:
                content = self.text_edit.toPlainText()
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(content)
                    self.current_file_path = file_path
                    self.update_window_title()
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

    def update_translation_output(self, translated_text):
        self.translation_output.setPlainText(translated_text)

    def start_translation_thread(self, text):
        self.translation_output.setPlainText("Translating...")
        translator = self.translator_combo.currentText()
        language = self.language_combo.currentText()

        self.worker = TranslationWorker(text, translator, language, self.llm_url)
        self.thread = threading.Thread(target=self.worker.run)
        self.worker.finished.connect(self.update_translation_output)
        self.thread.start()