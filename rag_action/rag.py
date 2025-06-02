import hashlib
import json
import logging
import os
import re
import yaml
from langchain import hub
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.text_splitter import TextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.document_loaders.base import BaseLoader
from supabase import Client  # type: ignore
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MarkdownFrontmatterLoader(BaseLoader):
    def __init__(self, file_path):
        """Load a markdown file and parse YAML frontmatter to document metadata."""
        self.file_path = file_path

    def load(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Regex to extract frontmatter block
        pattern = r"^---\s*\n(.*?\n?)^---\s*\n"  # Non-greedy, multiline
        match = re.search(pattern, text, flags=re.DOTALL | re.MULTILINE)
        metadata = {}
        body = text
        if match:
            frontmatter = match.group(1)
            metadata = yaml.safe_load(frontmatter) or {}
            body = text[match.end() :]

        # Return Document with extracted metadata
        return [Document(page_content=body.strip(), metadata=metadata)]


def model_chat(question: str, context: str, model: str) -> str:
    """
    Perform a chat with the model.
    """
    os.environ["LANGCHAIN_API_KEY"] = "dummy_key"
    prompt = hub.pull("rlm/rag-prompt")
    llm = init_chat_model(model=model)
    messages = prompt.invoke({"question": question, "context": context})
    response = llm.invoke(messages)
    return response.content


def apply_metadata(docs: List[Document], metadata: dict) -> List[Document]:
    """
    Apply metadata to a list of Document objects.
    """
    for doc in docs:
        new_metadata = metadata.copy()
        new_metadata.update(doc.metadata or {})
        doc.metadata = json.loads(json.dumps(new_metadata, default=str))
    return docs


def chunk_documents(
    docs: List[Document], text_splitter: TextSplitter
) -> List[Document]:
    """
    Split documents into smaller chunks.
    """
    chunks = []
    for doc in docs:
        splits = text_splitter.split_documents([doc])
        chunks.extend(splits)
    logger.debug(f"Chunked to {len(chunks)} segments")
    return chunks


def get_openai_embeddings(model: str, api_key: str) -> OpenAIEmbeddings:
    """
    Get OpenAI embeddings instance.
    """
    return OpenAIEmbeddings(model=model, api_key=api_key)


def format_rag_documents(docs: List[Document]) -> str:
    """
    Format a list of Document objects into a string for RAG.
    """
    formatted_docs = []
    for doc in docs:
        metadata_str = json.dumps(doc.metadata, separators=(",", ":"), indent=None)
        content_str = doc.page_content.replace("\n", " ").strip()
        formatted_docs.append(f"Content:\n{content_str}\n\nMetadata: {metadata_str}")
    return "\n\n\n".join(formatted_docs)


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


def supabase_query(
    query: str,
    supabase_client: Client,
    db_table: str,
    embeddings: OpenAIEmbeddings,
    filter: Optional[Dict[str, Any]] = None,
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
    docs = vectorstore.similarity_search(query, top_k, filter)
    logger.info(
        f"Vector Store Query: table='{db_table}' query='{query}' filter={filter} top_k={top_k} found={len(docs)}"
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
