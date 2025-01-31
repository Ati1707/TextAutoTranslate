import argparse
import sys
from PySide6.QtWidgets import QApplication
from app import TranslatorApp

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TextAutoTranslate Application')
    parser.add_argument('--llm-url',
                        default='http://localhost:5001/api/v1/generate',
                        help='URL for the LLM translation API')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = TranslatorApp(llm_url=args.llm_url)
    window.show()
    sys.exit(app.exec())