from openai import OpenAI
import os

class OpenAIManager:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4.1"

    def test_connection(self):
        try:
            response = self.client.responses.create(
                model=self.model,
                input="Test connection",
                max_output_tokens=10
            )
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)
