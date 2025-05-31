import logging
from ..rag import (
    chunk_documents,
    parse_metadata,
    get_openai_embeddings,
    build_document_embeddings,
    store_in_supabase,
    ingest_directory,
)
from ..supabase import create_client as create_supabase_client
from ..utils import setup_logger, introduce

setup_logger()
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    from ..config import base_config, get_env_var

    chunk_size = get_env_var("CHUNK_SIZE", 1000, int)
    chunk_overlap = get_env_var("CHUNK_OVERLAP", 200, int)
    ingest_dir_input = get_env_var("INGEST_DIR")
    ingest_glob_pattern = get_env_var("INGEST_GLOB_PATTERN", "*.*")
    ingest_metadata = get_env_var("INGEST_METADATA", "{}")

    metadata = parse_metadata(ingest_metadata)

    logger.info(
        introduce(
            "Ingest Directory",
            base_config,
            {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "ingest_dir_input": ingest_dir_input,
                "ingest_glob_pattern": ingest_glob_pattern,
                "ingest_metadata": ingest_metadata,
            },
            metadata,
        )
    )

    openai_embeddings = get_openai_embeddings(
        model=base_config.embedding_model, api_key=base_config.openai_api_key
    )
    supabase_client = create_supabase_client(
        base_config.supabase_url, base_config.supabase_key
    )

    documents = ingest_directory(ingest_dir_input, metadata, ingest_glob_pattern)

    chunks = chunk_documents(
        documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    doc_embeddings = build_document_embeddings(chunks, openai_embeddings)

    store_in_supabase(
        chunks,
        doc_embeddings,
        supabase_client=supabase_client,
        db_table=base_config.supabase_table,
    )

    logger.info("Done!")
