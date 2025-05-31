import logging
from ..rag import model_chat
from ..utils import setup_logger, introduce, set_action_ouput

setup_logger()
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    from ..config import base_config, get_env_var

    prompt_text_input = get_env_var("PROMPT_TEXT")
    chat_model = get_env_var("CHAT_MODEL")

    logger.info(
        introduce(
            "Infer Chat",
            base_config,
            {
                "prompt_text": prompt_text_input,
                "chat_model": chat_model,
            },
        )
    )

    response = model_chat(prompt_text_input, chat_model)

    logger.info(f"Chat Response: {response.content}")
    set_action_ouput("text_base64", response.content)
