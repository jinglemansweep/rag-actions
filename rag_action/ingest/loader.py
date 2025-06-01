import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
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

DEFAULT_LOADER_CLASS = "markdown"
DEFAULT_LOADER_OPTIONS = {"glob_pattern": "**/*.md", "metadata": {}}

DEFAULT_CHUNKER_CLASS = "recursive_character"
DEFAULT_CHUNKER_OPTIONS = {"chunk_size": 1000, "chunk_overlap": 200}

if __name__ == "__main__":

    openai_api_key = get_env_var("OPENAI_API_KEY")
    supabase_url = get_env_var("SUPABASE_URL")
    supabase_key = get_env_var("SUPABASE_KEY")
    supabase_table = get_env_var("SUPABASE_TABLE")
    embedding_model = get_env_var("EMBEDDING_MODEL")
    loader_class = get_env_var("LOADER_CLASS", default=DEFAULT_LOADER_CLASS)
    loader_options_str = get_env_var("LOADER_OPTIONS", "{}")
    loader_options = DEFAULT_LOADER_OPTIONS | parse_json(loader_options_str)
    chunker_model = get_env_var("CHUNKER_MODEL", default=DEFAULT_CHUNKER_CLASS)
    chunker_options_str = get_env_var("CHUNKER_OPTIONS", "{}")
    chunker_options = DEFAULT_CHUNKER_OPTIONS | parse_json(chunker_options_str)

    logger.info(f"OPENAI: model={embedding_model}")
    logger.info(f"SUPABASE: url={supabase_url} table={supabase_table}")
    logger.info(f"LOADER: options={loader_options}")
    logger.info(f"CHUNKER: options={chunker_options}")

    openai_embeddings = get_openai_embeddings(
        model=embedding_model, api_key=openai_api_key
    )

    supabase_client = create_supabase_client(supabase_url, supabase_key)

    documents = ingest_directory(
        loader_options["directory"],
        loader_options["metadata"],
        loader_options["glob_pattern"],
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunker_options["chunk_size"],
        chunk_overlap=chunker_options["chunk_overlap"],
        separators=["\n\n", "\n", ".", "!", "?", " ", ""],
    )

    chunks = chunk_documents(documents, text_splitter)

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
