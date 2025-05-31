import logging
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

    from ..config import base_config, get_env_var

    chunk_size = get_env_var("CHUNK_SIZE", 2000, int)
    chunk_overlap = get_env_var("CHUNK_OVERLAP", 200, int)
    ingest_text_input = get_env_var("INGEST_TEXT")
    ingest_metadata = get_env_var("INGEST_METADATA", "{}")

    metadata = parse_metadata(ingest_metadata, base_config.supabase_collection)

    logger.info(
        introduce(
            "Vector Store Ingest - Text",
            base_config,
            {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "ingest_text_input": ingest_text_input,
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
        db_table=base_config.supabase_table,
    )
