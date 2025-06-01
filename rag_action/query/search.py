import logging
from ..config import get_env_var
from ..rag import get_openai_embeddings, supabase_query, docs_json
from ..supabase import create_client as create_supabase_client
from ..utils import setup_logger, introduce, set_action_ouput

setup_logger()
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    openai_api_key = get_env_var("OPENAI_API_KEY")
    supabase_url = get_env_var("SUPABASE_URL")
    supabase_key = get_env_var("SUPABASE_KEY")
    supabase_table = get_env_var("SUPABASE_TABLE")
    supabase_collection = get_env_var("SUPABASE_COLLECTION")

    embedding_model = get_env_var("EMBEDDING_MODEL", "text-embedding-ada-002")
    query_text_input = get_env_var("QUERY_TEXT")
    top_k = get_env_var("TOP_K", "5", int)

    logger.info(
        introduce(
            "Vector Store Query",
            {
                "openai_api_key": openai_api_key,
                "supabase_url": supabase_url,
                "supabase_key": supabase_key,
                "supabase_table": supabase_table,
                "supabase_collection": supabase_collection,
                "embedding_model": "text-embedding-ada-002",
                "query_text": query_text_input,
                "top_k": top_k,
            },
        )
    )

    openai_embeddings = get_openai_embeddings(
        model=embedding_model, api_key=openai_api_key
    )
    supabase_client = create_supabase_client(supabase_url, supabase_key)

    documents = supabase_query(
        query_text_input,
        supabase_client=supabase_client,
        db_table=supabase_table,
        db_collection=supabase_collection,
        embeddings=openai_embeddings,
        top_k=top_k,
    )

    set_action_ouput("json", {"docs": docs_json(documents)}, output_json=True)
