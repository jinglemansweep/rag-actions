import hashlib
import logging
import os
import sys
import glob
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader  # , UnstructuredURLLoader
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from supabase import create_client, Client  # type: ignore
from typing import List
from .utils import setup_logger

setup_logger(os.getenv("LOG_LEVEL", "info").lower())
logger = logging.getLogger(__name__)


def load_directory(directory: str, pattern="*.md") -> List[Document]:
    docs: List[Document] = []
    if settings.content_dir:
        for file_path in glob.glob(os.path.join(directory, pattern)):
            print(f"Loading file: {file_path}")
            docs.extend(TextLoader(file_path).load())
    else:
        logger.warning("No CONTENT_DIR specified.")
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
    db_url: str,
    db_table: str,
    api_key: str,
) -> None:
    supabase: Client = create_client(db_url, api_key)
    for chunk, vector in zip(chunks, vectors):
        chunk_hash = compute_chunk_hash(chunk.page_content)
        # Query for this hash
        existing = (
            supabase.table(db_table).select("id").eq("chunk_hash", chunk_hash).execute()
        )
        if existing.data:
            logger.info(f"Skipping duplicate chunk (hash: {chunk_hash})")
            continue
        logger.info(f"Inserting new chunk (hash: {chunk_hash})")
        data, count = (
            supabase.table(db_table)
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

    if settings.action_mode == "ingest":
        documents = load_directory(settings.content_dir)
    else:
        logger.fatal("Invalid ACTION_MODE. Use 'ingest' to load and process documents.")
        sys.exit(1)

    openai_embeddings = OpenAIEmbeddings(
        model=settings.embedding_model, api_key=settings.openai_api_key
    )

    supabase_client = create_client(settings.supabase_url, settings.supabase_key)

    vs_docs = query_vector_store(
        "Hello",
        supabase_client=supabase_client,
        db_table=settings.supabase_table,
        embeddings=openai_embeddings,
    )

    logger.info(f"Found {len(vs_docs)} documents in vector store.")

    chunks = chunk_documents(
        documents, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
    )

    embeddings = get_openai_embeddings(chunks, openai_embeddings)

    store_in_supabase(
        chunks,
        embeddings,
        db_url=settings.supabase_url,
        db_table=settings.supabase_table,
        api_key=settings.supabase_key,
    )

    logger.info("Done!")
