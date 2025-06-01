import logging
from langchain_community.document_loaders import DirectoryLoader, RSSFeedLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..config import get_env_var
from ..logger import setup_logger
from ..rag import (
    chunk_documents,
    apply_metadata,
    get_openai_embeddings,
    build_document_embeddings,
    supabase_write,
    MarkdownFrontmatterLoader,
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
    metadata = get_env_var("METADATA", "{}")
    metadata = parse_json(metadata)
    args_str = get_env_var("ARGS", "{}")
    args = parse_json(args_str)
    loader_class = get_env_var("LOADER_CLASS")
    loader_args_str = get_env_var("LOADER_ARGS", "{}")
    loader_args = parse_json(loader_args_str)
    chunker_class = get_env_var("CHUNKER_CLASS")
    chunker_args_str = get_env_var("CHUNKER_ARGS", "{}")
    chunker_args = parse_json(chunker_args_str)
    logger.info(f"OPENAI: model={embedding_model}")
    logger.info(f"SUPABASE: url={supabase_url} table={supabase_table}")
    logger.info(f"ACTION: args={args}")
    logger.info(f"LOADER: args={loader_args}")
    logger.info(f"CHUNKER: args={chunker_args}")

    openai_embeddings = get_openai_embeddings(
        model=embedding_model, api_key=openai_api_key
    )

    supabase_client = create_supabase_client(supabase_url, supabase_key)

    use_directory_loader = loader_class in ["markdown"]

    if loader_class == "SOMETHING_ELSE":
        raise NotImplementedError(f"Loader class '{loader_class}' is not implemented.")
    elif loader_class == "rss":
        loader_cls = RSSFeedLoader
    else:  # loader_class == "markdown"
        loader_cls = MarkdownFrontmatterLoader

    if use_directory_loader:
        loader = DirectoryLoader(
            loader_cls=loader_cls, loader_kwargs=loader_args, **args
        )
    else:
        loader = loader_cls(**loader_args)

    docs = loader.load()
    docs = apply_metadata(docs, metadata)

    if chunker_class == "SOMETHING_ELSE":
        raise NotImplementedError(
            f"Chunker class '{chunker_class}' is not implemented."
        )
    else:
        chunker_class = RecursiveCharacterTextSplitter

    chunker_inst = chunker_class(**chunker_args)
    chunks = chunk_documents(docs, chunker_inst)
    doc_embeddings = build_document_embeddings(chunks, openai_embeddings)

    supabase_write(
        chunks,
        doc_embeddings,
        supabase_client=supabase_client,
        db_table=supabase_table,
    )

    logger.info(
        f"Successfully ingested {len(docs)} documents and {len(chunks)} chunks."
    )
