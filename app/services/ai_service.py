import requests

from flask import current_app


class AIServiceError(Exception):
    """Yapay zeka servisi hatalari icin ozel hata sinifi."""
    pass


class AIService:
    def _get_system_prompt(self):
        return current_app.config["BUSINESS_CONTEXT"]

    def _get_api_key(self):
        return current_app.config.get("GROQ_API_KEY", "")

    def yanit_uret(self, mesaj, gecmis=None):
        """
        Kullanicinin mesajini Groq API'ye gonderir ve cevabi dondurur.
        API anahtari yoksa demo modu mesaji verir.
        """
        if gecmis is None:
            gecmis = []

        api_key = self._get_api_key()

        if not api_key:
            return (
                "TANAXIS AI şu anda demo modunda çalışıyor. "
                "Sorunuzu aldım; canlı yapay zekâ yanıtları için API anahtarının "
                "tanımlanması gerekiyor."
            )

        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            }
        ]

        for item in gecmis:
            if (
                isinstance(item, dict)
                and "role" in item
                and "content" in item
            ):
                messages.append(item)

        messages.append(
            {
                "role": "user",
                "content": mesaj
            }
        )

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-oss-20b",
                    "messages": messages,
                    "temperature": 0.5,
                    "max_tokens": 1200
                },
                timeout=30
            )

            if response.status_code != 200:
                raise AIServiceError(
                    f"Groq API hata kodu: {response.status_code} - {response.text}"
                )

            data = response.json()

            return data["choices"][0]["message"]["content"]

        except requests.RequestException as exc:
            raise AIServiceError(
                "Yapay zeka servisine baglanirken bir hata olustu."
            ) from exc

        except (KeyError, IndexError, TypeError) as exc:
            raise AIServiceError(
                "Yapay zeka servisinden beklenmeyen bir yanit alindi."
            ) from exc


ai_service = AIService()