import logging
from ..rag import (
    chunk_documents,
    parse_metadata,
    get_openai_embeddings,
    build_document_embeddings,
    supabase_write,
    ingest_directory,
)
from ..config import get_env_var
from ..supabase import create_client as create_supabase_client
from ..utils import setup_logger

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
    ingest_dir_input = get_env_var("INGEST_DIR")
    ingest_glob_pattern = get_env_var("INGEST_GLOB_PATTERN", "*.*")
    ingest_metadata = get_env_var("INGEST_METADATA", "{}")

    metadata = parse_metadata(ingest_metadata, supabase_collection)

    openai_embeddings = get_openai_embeddings(
        model=embedding_model, api_key=openai_api_key
    )
    supabase_client = create_supabase_client(supabase_url, supabase_key)

    documents = ingest_directory(ingest_dir_input, metadata, ingest_glob_pattern)

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

    logger.info(
        f"Successfully ingested {len(documents)} documents and {len(chunks)} chunks."
    )
