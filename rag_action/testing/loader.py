import logging
from langchain_core.documents import Document
from ..constants import StateMessage
from ..github import get_action_input, set_action_output
from ..utils import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

DOCS = [
    Document(
        page_content="This is a sample document.", metadata={"source": "example_source"}
    ),
    Document(
        page_content="This is another sample document.",
        metadata={"source": "another_source"},
    ),
]


if __name__ == "__main__":

    input_state = get_action_input()

    set_action_output(
        StateMessage(
            docs=input_state.docs,
            outputs={"test_output": "result"},
            metadata={"test_metadata": "info"},
        )
    )
