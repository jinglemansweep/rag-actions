import logging
from ..config import get_env_var
from ..logger import setup_logger
from ..rag import (
    format_rag_documents,
    get_openai_embeddings,
    model_chat,
    supabase_query,
)
from ..supabase import create_client as create_supabase_client
from ..utils import parse_json

setup_logger()
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    openai_api_key = get_env_var("OPENAI_API_KEY")
    supabase_url = get_env_var("SUPABASE_URL")
    supabase_key = get_env_var("SUPABASE_KEY")
    supabase_table = get_env_var("SUPABASE_TABLE")
    supabase_filter_str = get_env_var("SUPABASE_FILTER", "{}")
    supabase_filter = parse_json(supabase_filter_str)
    top_k = int(get_env_var("TOP_K"))
    chat_model = get_env_var("CHAT_MODEL")
    chat_prompt = get_env_var("CHAT_PROMPT")
    embedding_model = get_env_var("EMBEDDING_MODEL")

    logger.info(
        f"OPENAI: chat_model={chat_model} embedding_model={embedding_model} chat_prompt={chat_prompt[:40]}..."
    )
    logger.info(
        f"SUPABASE: url={supabase_url} table={supabase_table} filter={supabase_filter}"
    )
    logger.info(f"ACTION: top_k={top_k}")

    openai_embeddings = get_openai_embeddings(
        model=embedding_model, api_key=openai_api_key
    )

    supabase_client = create_supabase_client(supabase_url, supabase_key)

    docs = supabase_query(
        chat_prompt,
        supabase_client,
        supabase_table,
        openai_embeddings,
        supabase_filter,
        top_k,
    )
    formatted_docs = format_rag_documents(docs)

    response = model_chat(chat_prompt, formatted_docs, chat_model)

    logger.info(f"Response: {response}")
