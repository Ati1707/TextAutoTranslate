import requests


class KoboldCPPProvider:
    def __init__(self, api_url):
        self.api_url = api_url

    def translate(self, text, source_lang=None, target_lang="English"):
        source_part = (
            f"{source_lang.upper()}-LANGUAGE TEXT"
            if source_lang
            else "AUTO-DETECTED LANGUAGE TEXT"
        )

        target_part = (
            target_lang.upper()
            if target_lang != "English"  # Handle case-insensitive check
            else "ENGLISH"
        )

        lang_instruction = (
            f"TRANSLATE THIS {source_part} TO {target_part}\n"
            "PRESERVE NUMBERS/NAMES/SPECIAL TERMS AND USE NATURAL FLOW"
        )

        prompt = f"""Execute this translation task precisely:

1. {lang_instruction}
2. OUTPUT MUST BE:
   - PURE TRANSLATION ONLY
   - NO EXPLANATIONS
   - NO FORMATTING
   - NO MARKDOWN
   - NO QUOTES
3. IF INPUT IS ENGLISH, OUTPUT IDENTICAL TEXT
4. PRESERVE NUMBERS/NAMES/SPECIAL TERMS
5. RESPONSE MUST BE 1 PARAGRAPH, NO LINE BREAKS

INPUT: "{text}"

TRANSLATION OUTPUT: """

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
            "typical": 1
        }

        response = requests.post(
            self.api_url,
            json=data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return response.json()["results"][0]["text"]
        raise Exception(f"API request failed ({response.status_code})")