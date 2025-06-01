import logging
from ..config import get_env_var
from ..rag import (
    chunk_documents,
    parse_metadata,
    get_openai_embeddings,
    build_document_embeddings,
    supabase_write,
    ingest_text,
)
from ..supabase import create_client as create_supabase_client
from ..utils import setup_logger, introduce

setup_logger()
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    openai_api_key = get_env_var("OPENAI_API_KEY")
    supabase_url = get_env_var("SUPABASE_URL")
    supabase_key = get_env_var("SUPABASE_KEY")
    supabase_table = get_env_var("SUPABASE_TABLE")
    supabase_collection = get_env_var("SUPABASE_COLLECTION")

    embedding_model = get_env_var("EMBEDDING_MODEL", "text-embedding-ada-002")
    chunk_size = get_env_var("CHUNK_SIZE", 10000, int)
    chunk_overlap = get_env_var("CHUNK_OVERLAP", 200, int)
    ingest_text_input = get_env_var("INGEST_TEXT")
    ingest_metadata = get_env_var("INGEST_METADATA", "{}")

    metadata = parse_metadata(ingest_metadata, supabase_collection)

    logger.info(
        introduce(
            "Vector Store Ingest - Text",
            {
                "openai_api_key": openai_api_key,
                "supabase_url": supabase_url,
                "supabase_key": supabase_key,
                "supabase_table": supabase_table,
                "supabase_collection": supabase_collection,
                "embedding_model": embedding_model,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "ingest_text_input": ingest_text_input,
                "ingest_metadata": ingest_metadata,
            },
            metadata,
        )
    )

    openai_embeddings = get_openai_embeddings(
        model=embedding_model, api_key=openai_api_key
    )
    supabase_client = create_supabase_client(supabase_url, supabase_key)

    documents = ingest_text(ingest_text_input, metadata)

    chunks = chunk_documents(
        documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    doc_embeddings = build_document_embeddings(chunks, openai_embeddings)

    supabase_write(
        chunks,
        doc_embeddings,
        supabase_client=supabase_client,
        db_table=supabase_table,
    )
