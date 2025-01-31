from translators import translate_text


class GoogleTranslator:
    @staticmethod
    def translate(text, target_lang="en", **kwargs):
        return translate_text(text, translator="google", to_language=target_lang)
