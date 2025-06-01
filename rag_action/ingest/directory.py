import logging
from ..config import get_env_var
from ..logger import setup_logger
from ..rag import (
    chunk_documents,
    get_openai_embeddings,
    build_document_embeddings,
    supabase_write,
    ingest_directory,
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
    embedding_model = get_env_var("EMBEDDING_MODEL")
    chunk_size = get_env_var("CHUNK_SIZE", cast_type=int)
    chunk_overlap = get_env_var("CHUNK_OVERLAP", cast_type=int)
    directory = get_env_var("DIRECTORY")
    glob_pattern = get_env_var("GLOB_PATTERN")
    metadata_str = get_env_var("METADATA", "{}")
    metadata = parse_json(metadata_str)

    logger.info(f"OPENAI: model={embedding_model}")
    logger.info(f"SUPABASE: url={supabase_url} table={supabase_table}")
    logger.info(f"INGEST: dir={directory} glob={glob_pattern} metadata={metadata}")
    logger.info(f"CHUNKING: chunk_size={chunk_size} chunk_overlap={chunk_overlap}")

    openai_embeddings = get_openai_embeddings(
        model=embedding_model, api_key=openai_api_key
    )

    supabase_client = create_supabase_client(supabase_url, supabase_key)

    documents = ingest_directory(directory, metadata, glob_pattern)

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
