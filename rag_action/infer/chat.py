import logging
from ..constants import StateMessage
from ..config import get_env_var
from ..github import get_action_input, set_action_output
from ..rag import model_chat
from ..utils import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    openai_api_key = get_env_var("OPENAI_API_KEY")
    prompt_text_input = get_env_var("PROMPT_TEXT")
    chat_model = get_env_var("CHAT_MODEL")

    input_state = get_action_input()

    response = model_chat(prompt_text_input, chat_model)

    set_action_output(
        StateMessage(
            outputs={"response": response.content},
            metadata={"prompt_text": prompt_text_input, "chat_model": chat_model},
        )
    )
