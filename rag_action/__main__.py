import hashlib
import json
import logging
import os
import sys
import glob
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader  # , UnstructuredURLLoader
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from pathlib import Path
from supabase import create_client, Client  # type: ignore
from typing import Dict, List
from .utils import setup_logger

setup_logger(os.getenv("LOG_LEVEL", "info").lower())
logger = logging.getLogger(__name__)


def ingest_directory(directory: str, metadata: Dict, pattern="*.md") -> List[Document]:
    docs: List[Document] = []
    if Path(settings.ingest_dir).exists():
        for file_path in glob.glob(os.path.join(directory, pattern)):
            logger.info(f"Loading file: {file_path}")
            docs.extend(TextLoader(file_path).load())
    else:
        logger.warning("No CONTENT_DIR specified.")
    for doc in docs:
        doc_metadata = metadata.copy()
        doc_metadata.update(doc.metadata or {})
        doc_metadata["loader"] = "directory"
        doc.metadata = doc_metadata
    return docs


def ingest_text(text: str, metadata: Dict) -> List[Document]:
    docs = [Document(page_content=settings.ingest_text, metadata=metadata)]
    for doc in docs:
        doc_metadata = metadata.copy()
        doc_metadata.update(doc.metadata or {})
        doc_metadata["loader"] = "text"
        doc.metadata = doc_metadata
    return docs


def chunk_documents(
    docs: List[Document], chunk_size: int, chunk_overlap: int
) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""],
    )
    chunks = []
    for doc in docs:
        splits = splitter.split_documents([doc])
        chunks.extend(splits)
    logger.info(f"Chunked to {len(chunks)} segments")
    return chunks


def get_openai_embeddings(
    texts: List[Document], embeddings: OpenAIEmbeddings
) -> List[List[float]]:
    return embeddings.embed_documents([chunk.page_content for chunk in texts])


def compute_chunk_hash(text: str) -> str:
    """
    Compute a hash of chunk text for deduplication.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def query_vector_store(
    query: str,
    supabase_client: Client,
    db_table: str,
    embeddings: OpenAIEmbeddings,
    top_k: int = 5,
) -> List[Document]:
    vectorstore = SupabaseVectorStore(
        client=supabase_client,
        table_name=db_table,
        embedding=embeddings,
        query_name="match_documents",
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    return retriever.invoke(query)


def store_in_supabase(
    chunks: List[Document],
    vectors: List[List[float]],
    supabase_client: Client,
    db_table: str,
) -> None:
    for chunk, vector in zip(chunks, vectors):
        chunk_hash = compute_chunk_hash(chunk.page_content)
        # Query for this hash
        existing = (
            supabase_client.table(db_table)
            .select("id")
            .eq("chunk_hash", chunk_hash)
            .execute()
        )
        if existing.data:
            logger.info(f"Skipping duplicate chunk (hash: {chunk_hash})")
            continue
        logger.info(f"Inserting new chunk (hash: {chunk_hash})")
        data, count = (
            supabase_client.table(db_table)
            .insert(
                [
                    {
                        "content": chunk.page_content,
                        "metadata": chunk.metadata,
                        "chunk_hash": chunk_hash,
                        "embedding": vector,
                    }
                ]
            )
            .execute()
        )


if __name__ == "__main__":

    from .config import settings

    openai_embeddings = OpenAIEmbeddings(
        model=settings.embedding_model, api_key=settings.openai_api_key
    )

    supabase_client = create_client(settings.supabase_url, settings.supabase_key)

    if settings.action_mode == "query":

        if len(settings.query_text) > 0:
            vs_docs = query_vector_store(
                settings.query_text,
                supabase_client=supabase_client,
                db_table=settings.supabase_table,
                embeddings=openai_embeddings,
                top_k=2,
            )
            print(vs_docs)
            logger.info(f"Found {len(vs_docs)} documents in vector store.")

        else:
            logger.fatal("No query text provided, set QUERY_TEXT environment variable")
            sys.exit(1)

    elif settings.action_mode == "ingest":

        try:
            metadata = (
                json.loads(settings.ingest_metadata) if settings.ingest_metadata else {}
            )
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in ingest_metadata: {e}")
            metadata = {}
        logger.info(f"Metadata for ingestion: {metadata}")

        if len(settings.ingest_dir) > 0 and Path(settings.ingest_dir).exists():
            documents = ingest_directory(
                settings.ingest_dir, metadata, settings.ingest_pattern
            )
        elif len(settings.ingest_text) > 0:
            documents = ingest_text(settings.ingest_text, metadata)

        else:
            logger.fatal(
                "No content to ingest, set INGEST_DIR or INGEST_TEXT environment variables"
            )
            sys.exit(1)

        chunks = chunk_documents(
            documents,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        embeddings = get_openai_embeddings(chunks, openai_embeddings)

        store_in_supabase(
            chunks,
            embeddings,
            supabase_client=supabase_client,
            db_table=settings.supabase_table,
        )

    else:
        logger.fatal("Invalid ACTION_MODE. Use 'ingest' to load and process documents.")
        sys.exit(1)

    logger.info("Done!")
