import glob
import hashlib
import logging
import os
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import TextLoader  # , UnstructuredURLLoader
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from pathlib import Path
from supabase import Client  # type: ignore
from typing import Dict, List

logger = logging.getLogger(__name__)


def model_chat(prompt: str, chat_model: str) -> BaseMessage:
    """
    Perform a chat with the model.
    """
    llm = init_chat_model(model=chat_model)
    response = llm.invoke(prompt)
    return response


def chunk_documents(
    docs: List[Document], chunk_size: int, chunk_overlap: int
) -> List[Document]:
    """
    Split documents into smaller chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""],
    )
    chunks = []
    for doc in docs:
        splits = splitter.split_documents([doc])
        chunks.extend(splits)
    logger.debug(f"Chunked to {len(chunks)} segments")
    return chunks


def get_openai_embeddings(model: str, api_key: str) -> OpenAIEmbeddings:
    """
    Get OpenAI embeddings instance.
    """
    return OpenAIEmbeddings(model=model, api_key=api_key)


def build_document_embeddings(
    docs: List[Document], embeddings: OpenAIEmbeddings
) -> List[List[float]]:
    """
    Get embeddings for a list of Document objects.
    """
    return embeddings.embed_documents([doc.page_content for doc in docs])


def compute_chunk_hash(text: str) -> str:
    """
    Compute a hash of chunk text for deduplication.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_metadata_filter(db_collection: str) -> dict:
    """
    Build a filter for querying documents.
    This can be customized based on your requirements.
    """
    return {"_collection": db_collection}


def supabase_query(
    query: str,
    supabase_client: Client,
    db_table: str,
    db_collection: str,
    embeddings: OpenAIEmbeddings,
    top_k: int = 5,
) -> List[Document]:
    """
    Query the Supabase vector store for similar documents.
    """
    vectorstore = SupabaseVectorStore(
        client=supabase_client,
        table_name=db_table,
        embedding=embeddings,
        query_name="match_documents",
    )
    filter = build_metadata_filter(db_collection)
    docs = vectorstore.similarity_search(query, top_k, filter)
    logger.info(
        f"Vector Store Query: table='{db_table}' collection='{db_collection}' query='{query}' top_k={top_k} found={len(docs)}"
    )
    return docs


def supabase_write(
    chunks: List[Document],
    vectors: List[List[float]],
    supabase_client: Client,
    db_table: str,
) -> None:
    """
    Store chunks and their embeddings in Supabase.
    """
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


def ingest_directory(directory: str, metadata: Dict, pattern="*.md") -> List[Document]:
    """
    Ingest documents from a directory, loading files matching the pattern.
    """
    docs: List[Document] = []
    if Path(directory).exists():
        for file_path in glob.glob(os.path.join(directory, pattern)):
            logger.info(f"Loading file: {file_path}")
            docs.extend(TextLoader(file_path).load())
    else:
        logger.warning("Directory does not exist, skipping ingestion")
    for doc in docs:
        doc_metadata = metadata.copy()
        doc_metadata.update(doc.metadata or {})
        doc_metadata["loader"] = "directory"
        doc.metadata = doc_metadata
    return docs


def ingest_text(text: str, metadata: Dict) -> List[Document]:
    """
    Ingest a single text string as a Document.
    """
    docs = [Document(page_content=text, metadata=metadata)]
    for doc in docs:
        doc_metadata = metadata.copy()
        doc_metadata.update(doc.metadata or {})
        doc_metadata["loader"] = "text"
        doc.metadata = doc_metadata
    return docs
