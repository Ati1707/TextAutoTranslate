from .base_translator import BaseTranslator


class BingTranslator(BaseTranslator):
    PROVIDER = "bing"


class GoogleTranslator(BaseTranslator):
    PROVIDER = "google"


class YandexTranslator(BaseTranslator):
    PROVIDER = "yandex"
