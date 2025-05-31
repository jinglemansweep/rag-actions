import logging
from ..rag import (
    get_openai_embeddings,
    supabase_query,
)
from ..supabase import create_client as create_supabase_client
from ..utils import setup_logger, introduce, set_action_ouput

setup_logger()
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    from ..config import base_config, get_env_var

    query_text_input = get_env_var("QUERY_TEXT")
    top_k = get_env_var("TOP_K", "5", int)

    logger.info(
        introduce(
            "Vector Store Query",
            base_config,
            {"query_text": query_text_input, "top_k": top_k},
        )
    )

    openai_embeddings = get_openai_embeddings(
        model=base_config.embedding_model, api_key=base_config.openai_api_key
    )
    supabase_client = create_supabase_client(
        base_config.supabase_url, base_config.supabase_key
    )

    documents = supabase_query(
        query_text_input,
        supabase_client=supabase_client,
        db_table=base_config.supabase_table,
        db_collection=base_config.supabase_collection,
        embeddings=openai_embeddings,
        top_k=top_k,
    )

    logger.info(f"Found {len(documents)} documents for query: {query_text_input}")
    logger.info("Documents:\n\n{documents}")
    set_action_ouput("json", {"documents": documents}, output_json=True)
