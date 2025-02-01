import translators
from translators import translate_text


class BaseTranslator:
    PROVIDER = None

    @classmethod
    def translate(cls, text, source_lang="auto", target_lang="en"):
        return translate_text(
            text,
            translator=cls.PROVIDER,
            from_language=source_lang,
            to_language=target_lang,
        )

    @classmethod
    def get_language_map(cls):
        return translators.get_languages(cls.PROVIDER)
