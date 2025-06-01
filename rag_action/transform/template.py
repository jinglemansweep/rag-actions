import logging
from jinja2 import Template
from ..constants import StateMessage
from ..config import get_env_var
from ..github import get_action_input, set_action_output
from ..utils import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    template_text_input = get_env_var("TEMPLATE_TEXT")
    input_json = get_action_input()

    rendered = Template(template_text_input).render(json=input_json)

    set_action_output(StateMessage(outputs={"text": rendered}))
