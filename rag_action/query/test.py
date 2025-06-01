import json
import logging
from ..config import get_env_var
from ..utils import setup_logger, introduce, set_action_ouput

setup_logger()
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    openai_api_key = get_env_var("OPENAI_API_KEY")
    supabase_url = get_env_var("SUPABASE_URL")
    supabase_key = get_env_var("SUPABASE_KEY")
    supabase_table = get_env_var("SUPABASE_TABLE")
    supabase_collection = get_env_var("SUPABASE_COLLECTION")

    input_json_text = get_env_var("JSON", "{}")
    try:
        input_json = json.loads(input_json_text)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON input: {e}")
        input_json = {}

    logger.info(
        introduce(
            "Test",
            {
                "openai_api_key": openai_api_key,
                "supabase_url": supabase_url,
                "supabase_key": supabase_key,
                "supabase_table": supabase_table,
                "supabase_collection": supabase_collection,
                "embedding_model": "text-embedding-ada-002",
                "json": input_json,
            },
        )
    )

    input_json["modified"] = "HelloWorld"

    set_action_ouput("json", input_json, output_json=True)
