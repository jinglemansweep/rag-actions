import logging
from jinja2 import Template
from ..config import get_env_var
from ..utils import setup_logger, introduce, get_action_input, set_action_output

setup_logger()
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    template_text_input = get_env_var("TEMPLATE_TEXT")
    input_json = get_action_input()

    logger.info(
        introduce(
            "Transform Template",
            {
                "template_text": template_text_input,
                "json": input_json,
            },
        )
    )

    rendered = Template(template_text_input).render(json=input_json)

    logger.info(f"Output:\n\n{rendered}")
    set_action_output({"text": rendered})
