import requests


class KoboldCPPProvider:
    def __init__(self, api_url):
        self.api_url = api_url

    def translate(self, text, source_lang=None, target_lang="English"):
        source_part = f"{source_lang.upper()}" if source_lang else "CHINESE"

        target_part = (
            target_lang.upper()
            if target_lang != "English"  # Handle case-insensitive check
            else "ENGLISH"
        )

        prompt = f"""STRICT TRANSLATION TASK: {source_part} → {target_part}

        You are a professional translation engine. Your sole function is to convert Chinese text to English with absolute precision. Follow these directives without exception:

        1. MANDATORY OUTPUT FORMAT:
           - PURE TRANSLATION ONLY
           - NO CHINESE CHARACTERS IN OUTPUT
           - NO EXPLANATIONS/COMMENTARY
           - NO MARKDOWN/FORMATTING
           - NO QUOTES/BRACKETS
           - PRESERVE ALL NUMBERS/NAMES/SPECIAL TERMS
           - HANDLE SPECIAL CHARACTERS EXACTLY (%, $, ©, etc.)
           - SINGLE PARAGRAPH, NO LINE BREAKS

        2. CRITICAL RULES:
           - IF INPUT CONTAINS CHINESE, OUTPUT MUST BE ENGLISH
           - NEVER PRESERVE CHINESE CHARACTERS
           - TRANSLATE ALL TEXT, INCLUDING IDIOMS/PROVERBS
           - MAINTAIN ORIGINAL TEXT STRUCTURE
           - USE NATURAL, COLLOQUIAL ENGLISH

        3. FAILURE CONDITIONS:
           - CHINESE CHARACTERS IN OUTPUT = INCOMPLETE TRANSLATION
           - ADDED EXPLANATIONS = TASK FAILURE
           - FORMATTING DEVIATIONS = ERROR

        INPUT TEXT FOR TRANSLATION:
        {text}

        TRANSLATION OUTPUT:"""

        data = {
            "max_context_length": 4096,
            "max_length": 150,
            "prompt": prompt,
            "quiet": False,
            "rep_pen": 1.1,
            "rep_pen_range": 256,
            "rep_pen_slope": 1,
            "temperature": 0.5,
            "tfs": 1,
            "top_a": 0,
            "top_k": 100,
            "top_p": 1,
            "typical": 1,
        }

        response = requests.post(
            self.api_url, json=data, headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return response.json()["results"][0]["text"]
        raise Exception(f"API request failed ({response.status_code})")
