
import os
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiApiClient:
    """
    A client to interact with the Google Gemini API.
    """

    def __init__(self):
        """
        Initializes the Gemini API client.
        It configures the API key from environment variables.
        """
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def start_chat_session(self, system_prompt: str):
        """
        Starts a new chat session with a system prompt.

        Args:
            system_prompt: The initial system prompt to guide the conversation.

        Returns:
            A ChatSession object.
        """
        # The new API uses a `system_instruction` parameter in the model
        model_with_prompt = genai.GenerativeModel(
            'gemini-2.5-pro',
            system_instruction=system_prompt
        )
        return model_with_prompt.start_chat(history=[])

    def count_tokens(self, text: str) -> int:
        """
        Counts the number of tokens in a given text using the model's tokenizer.

        Args:
            text: The text to be tokenized.

        Returns:
            The total number of tokens.
        """
        return self.model.count_tokens(text).total_tokens

