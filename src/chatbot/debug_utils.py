
import pandas as pd
from tabulate import tabulate
from chatbot.gemini_api_client import GeminiApiClient

def analyze_prompt_token_usage(base_prompt: str, csv_data: dict[str, pd.DataFrame], user_question: str) -> dict:
    """
    Analyzes the token count for each component of the prompt.

    Args:
        base_prompt: The base system prompt text.
        csv_data: A dictionary where keys are filenames and values are pandas DataFrames.
        user_question: A sample user question.

    Returns:
        A dictionary with a detailed breakdown of token counts.
    """
    try:
        client = GeminiApiClient()
        model = client.model
    except Exception as e:
        return {"error": f"Could not initialize Gemini API client: {e}"}

    analysis = {}
    analysis['system_prompt_base'] = model.count_tokens(base_prompt).total_tokens
    analysis['user_question'] = model.count_tokens(user_question).total_tokens

    csv_tokens = {}
    total_csv_tokens = 0
    for name, df in csv_data.items():
        # We count tokens based on the final markdown representation
        markdown_table = tabulate(df, headers='keys', tablefmt='pipe')
        count = model.count_tokens(markdown_table).total_tokens
        csv_tokens[name] = count
        total_csv_tokens += count

    analysis['csv_data_breakdown'] = csv_tokens
    analysis['csv_data_total'] = total_csv_tokens

    # Calculate the grand total
    grand_total = analysis['system_prompt_base'] + analysis['user_question'] + total_csv_tokens
    analysis['grand_total'] = grand_total

    return analysis
