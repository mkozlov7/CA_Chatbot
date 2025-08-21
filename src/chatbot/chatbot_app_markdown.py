import streamlit as st
import os
import pandas as pd
import json
import random
from typing import Union, Dict
from tabulate import tabulate
from dotenv import load_dotenv
from chatbot.gemini_api_client import GeminiApiClient
from chatbot.logger_setup import detailed_logger, request_logger

# --- INITIALIZATION ---

load_dotenv()

PROMPT_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "config_data", "promotool_settings.md"))
SETTINGS_TABLES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "config_data", "settings_tables"))
WELCOME_MESSAGES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "config_data", "welcome_messages.json"))
FINAL_PROMPT_OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),"final_promt.md"))

# --- HELPER & LOGGING FUNCTIONS ---

def get_session_id() -> str:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    ctx = get_script_run_ctx()
    return ctx.session_id

def log_info(message: str, **kwargs):
    detailed_logger.info(message, extra={'session_id': get_session_id(), **kwargs})

def log_error(message: str, **kwargs):
    detailed_logger.error(message, extra={'session_id': get_session_id(), **kwargs})

# --- DATA LOADING FUNCTIONS ---

def load_csv_data_as_dfs() -> Dict[str, pd.DataFrame]:
    dataframes = {}
    try:
        for filename in sorted(os.listdir(SETTINGS_TABLES_PATH)):
            if filename.endswith(".csv"):
                file_path = os.path.join(SETTINGS_TABLES_PATH, filename)
                dataframes[filename] = pd.read_csv(file_path)
        return dataframes
    except FileNotFoundError:
        log_error(f"Settings tables directory not found at {SETTINGS_TABLES_PATH}")
        st.warning(f"Settings tables directory not found at {SETTINGS_TABLES_PATH}. Proceeding without table data.")
        return {}
    except Exception as e:
        log_error(f"Error loading CSV data: {e}")
        st.error(f"Error loading CSV data: {e}")
        return {}

def format_dfs_as_markdown(dataframes: Dict[str, pd.DataFrame]) -> str:
    all_tables_content = []
    for filename, df in dataframes.items():
        markdown_table = tabulate(df, headers='keys', tablefmt='pipe')
        all_tables_content.append(f"\n\n## {filename}\n\n{markdown_table}")
    return "".join(all_tables_content)

def load_and_enrich_system_prompt() -> Union[str, None]:
    try:
        with open(PROMPT_FILE_PATH, 'r', encoding='utf-8') as f:
            base_prompt = f.read()
        deep_analysis_instruction = ""
        target_section = "## Правила та Методологія Відповідей"
        enriched_prompt = base_prompt.replace(target_section, f"{target_section}\n\n{deep_analysis_instruction}")
        return enriched_prompt
    except FileNotFoundError:
        log_error(f"System prompt file not found at {PROMPT_FILE_PATH}")
        st.error(f"System prompt file not found at {PROMPT_FILE_PATH}")
        return None
    except Exception as e:
        log_error(f"Error loading system prompt: {e}")
        st.error(f"Error loading system prompt: {e}")
        return None

def get_random_welcome_message() -> str:
    try:
        with open(WELCOME_MESSAGES_PATH, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        return random.choice(messages)
    except (FileNotFoundError, IndexError, json.JSONDecodeError) as e:
        log_error(f"Could not load welcome messages: {e}")
        return "Hello! How can I help you with PromoTool today?"

# --- SESSION INITIALIZATION ---

def initialize_chat_session():
    if "chat_session" not in st.session_state:
        log_info("New user session started.")
        try:
            st.session_state.client = GeminiApiClient()
            enriched_prompt = load_and_enrich_system_prompt()
            if enriched_prompt:
                dfs = load_csv_data_as_dfs()
                tables_data_md = format_dfs_as_markdown(dfs)
                final_prompt = enriched_prompt + "\n\n---\n# Reference Data from Configuration Tables" + tables_data_md

                # Save final prompt to a file for debugging
                try:
                    with open(FINAL_PROMPT_OUTPUT_PATH, 'w', encoding='utf-8') as f:
                        f.write(final_prompt)
                    log_info(f"Successfully saved final prompt to {FINAL_PROMPT_OUTPUT_PATH}")
                except Exception as e:
                    log_error(f"Failed to save final prompt to file: {e}")
                
                # Live token count for the initial prompt
                initial_token_count = st.session_state.client.count_tokens(final_prompt)
                print(f"--- INITIAL PROMPT TOKEN COUNT: {initial_token_count} ---")
                log_info("Initial prompt token count", count=initial_token_count)

                st.session_state.chat_session = st.session_state.client.start_chat_session(final_prompt)
                log_info("Chat session initialized successfully.")
            else:
                st.session_state.chat_session = None
                log_error("Chat session initialization failed: Enriched prompt was empty.")
        except ValueError as e:
            log_error(f"Initialization failed: {e}")
            st.error(f"Initialization failed: {e}")
            st.session_state.chat_session = None
        except Exception as e:
            log_error(f"An unexpected error occurred during initialization: {e}")
            st.error(f"An unexpected error occurred during initialization: {e}")
            st.session_state.chat_session = None

# --- UI RENDERING ---

def main():
    st.set_page_config(page_title="PromoTool Chatbot", page_icon="🤖")
    st.title("🤖 PromoTool Assistant")
    st.caption("Я надаю підтримку з питань, що стосуються функціоналу та конфігурації PromoTool, використовуючи офіційну внутрішню інформацію")

    initialize_chat_session()

    if "messages" not in st.session_state:
        welcome_message = get_random_welcome_message()
        st.session_state.messages = [{"role": "assistant", "content": welcome_message}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_question := st.chat_input("Ask about PromoTool..."):
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        if st.session_state.chat_session is None:
            st.error("The chat session is not available. Please check your API key and system prompt file.")
            return

        with st.chat_message("assistant"):
            with st.spinner("Consulting the knowledge base..."):
                try:
                    log_info("User request", payload=user_question)
                    request_logger.info("request")

                    chat_session = st.session_state.chat_session
                    response = chat_session.send_message(user_question)
                    response_text = response.text

                    # Live token count for the current interaction
                    usage = response.usage_metadata
                    print(f"--- CURRENT TURN TOKEN USAGE ---")
                    print(f"  - Input (Question): {usage.prompt_token_count} tokens")
                    print(f"  - Output (Answer): {usage.candidates_token_count} tokens")
                    print(f"  - Total History (so far): {usage.total_token_count} tokens")
                    print("----------------------------")
                    log_info("LLM response", payload=response_text, usage=str(usage))

                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    log_error(f"An error occurred while communicating with the Gemini API: {e}")
                    st.error(f"An error occurred while communicating with the Gemini API: {e}")

if __name__ == "__main__":
    main()
