import getpass
import os
import time

import inquirer
import litellm

from ..utils.display_markdown_message import display_markdown_message


def validate_llm_settings(interpreter):
    """
    Interactivley prompt the user for required LLM settings
    """

    # This runs in a while loop so `continue` lets us start from the top
    # after changing settings (like switching to/from local)
    while True:
        if interpreter.local:
            # Ensure model is downloaded and ready to be set up

            if interpreter.model == "":
                # Interactive prompt to download the best local model we know of

                display_markdown_message(
                    """
                **Open Interpreter** will use `Mistral 7B` for local execution."""
                )

                if interpreter.gguf_quality == None:
                    interpreter.gguf_quality = 0.35

                """
                models = {
                    '7B': 'TheBloke/CodeLlama-7B-Instruct-GGUF',
                    '13B': 'TheBloke/CodeLlama-13B-Instruct-GGUF',
                    '34B': 'TheBloke/CodeLlama-34B-Instruct-GGUF'
                }

                parameter_choices = list(models.keys())
                questions = [inquirer.List('param', message="Parameter count (smaller is faster, larger is more capable)", choices=parameter_choices)]
                answers = inquirer.prompt(questions)
                chosen_param = answers['param']

                interpreter.model = "huggingface/" + models[chosen_param]
                """

                interpreter.model = "huggingface/TheBloke/Mistral-7B-Instruct-v0.1-GGUF"

                break

            else:
                # They have selected a model. Have they downloaded it?
                # Break here because currently, this is handled in llm/setup_local_text_llm.py
                # How should we unify all this?
                break

        else:
            # Ensure API keys are set as environment variables

            # OpenAI
            if interpreter.model in litellm.open_ai_chat_completion_models:
                if not os.environ.get("OPENAI_API_KEY") and not interpreter.api_key:
                    display_welcome_message_once()

                    display_markdown_message(
                        """---
                    > OpenAI API key not found

                    To use `GPT-4` (recommended) please provide an OpenAI API key.

                    To use `Mistral-7B` (free but less capable) press `enter`.
                    
                    ---
                    """
                    )

                    response = getpass.getpass("OpenAI API key: ")
                    print(f"OpenAI API key: {response[:4]}...{response[-4:]}")

                    if response == "":
                        # User pressed `enter`, requesting Mistral-7B
                        display_markdown_message(
                            """> Switching to `Mistral-7B`...
                        
                        **Tip:** Run `interpreter --local` to automatically use `Mistral-7B`.
                        
                        ---"""
                        )
                        time.sleep(1.5)
                        interpreter.local = True
                        interpreter.model = ""
                        continue

                    display_markdown_message(
                        """

                    **Tip:** To save this key for later, run `export OPENAI_API_KEY=your_api_key` on Mac/Linux or `setx OPENAI_API_KEY your_api_key` on Windows.
                    
                    ---"""
                    )

                    interpreter.api_key = response
                    time.sleep(2)
                    break

            # This is a model we don't have checks for yet.
            break

    # If we're here, we passed all the checks.

    # Auto-run is for fast, light useage -- no messages.
    # If mistral, we've already displayed a message.
    if not interpreter.auto_run and "mistral" not in interpreter.model.lower():
        display_markdown_message(f"> Model set to `{interpreter.model.upper()}`")
    return


def display_welcome_message_once():
    """
    Displays a welcome message only on its first call.

    (Uses an internal attribute `_displayed` to track its state.)
    """
    if not hasattr(display_welcome_message_once, "_displayed"):
        display_markdown_message(
            """
        ●

        Welcome to **Open Interpreter**.
        """
        )
        time.sleep(1.5)

        display_welcome_message_once._displayed = True
