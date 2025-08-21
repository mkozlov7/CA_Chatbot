
import os
import sys

# Add the src directory to the Python path to allow for absolute imports
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
sys.path.append(SRC_PATH)

from dotenv import load_dotenv
from chatbot.chatbot_app import load_and_enrich_system_prompt, load_csv_data_as_dfs
from chatbot.debug_utils import analyze_prompt_token_usage

def main():
    """
    Main function to run the token analysis and print the report.
    """
    print("Starting token usage analysis...")
    
    # Load environment variables to get the API key
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("\nERROR: GEMINI_API_KEY not found in .env file.")
        print("Please ensure you have a .env file in the project root with your key.")
        return

    # 1. Load all prompt components
    print("Loading prompt components...")
    base_prompt = load_and_enrich_system_prompt()
    if not base_prompt:
        print("Failed to load the system prompt. Aborting.")
        return
        
    csv_dfs = load_csv_data_as_dfs()
    if not csv_dfs:
        print("No CSV data found or failed to load. Analysis will be incomplete.")

    # Use a sample user question for a complete analysis
    sample_question = "Як працює kpi_CombinationToRecommendInOutOfGuideline?"

    # 2. Analyze token usage
    print("Analyzing token counts with Gemini API...")
    analysis_result = analyze_prompt_token_usage(base_prompt, csv_dfs, sample_question)

    if "error" in analysis_result:
        print(f"\nERROR: {analysis_result['error']}")
        return

    # 3. Print the report
    print("\n--- Token Usage Report ---")
    print(f"- Base System Prompt: {analysis_result['system_prompt_base']} tokens")
    print(f"- Sample User Question: {analysis_result['user_question']} tokens")
    print("\n--- CSV Data Breakdown ---")
    for name, count in analysis_result['csv_data_breakdown'].items():
        print(f"  - {name}: {count} tokens")
    print("--------------------------")
    print(f"- Total for CSV data: {analysis_result['csv_data_total']} tokens")
    print("==========================")
    print(f"GRAND TOTAL (for one request): {analysis_result['grand_total']} tokens")
    print("--------------------------\n")

if __name__ == "__main__":
    main()
