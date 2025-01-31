from PySide6.QtCore import QObject, Signal
from providers.translation.google import GoogleTranslator
from providers.llm.koboldcpp import KoboldCPPProvider


class TranslationWorker(QObject):
    finished = Signal(str)

    def __init__(self, text, translator, language, llm_url):
        super().__init__()
        self.text = text
        self.translator = translator
        self.language = language
        self.llm_url = llm_url

    def run(self):
        try:
            if self.translator == "Google":
                translated = GoogleTranslator.translate(self.text, target_lang="en")
            elif self.translator == "KoboldCPP":
                provider = KoboldCPPProvider(self.llm_url)
                translated = provider.translate(self.text, source_lang=self.language)
            else:
                raise ValueError("Unsupported translator")

            self.finished.emit(translated)
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")
