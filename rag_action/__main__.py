import hashlib
import os
import sys
import glob
from langchain_community.document_loaders import TextLoader, UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from supabase import create_client, Client  # type: ignore

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "rag_chunks")

DOCS_DIR = os.getenv("DOCS_DIR")
URL = os.getenv("URL")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))


def load_documents():
    docs = []
    if DOCS_DIR:
        for file_path in glob.glob(os.path.join(DOCS_DIR, "*.md")):
            print(f"Loading file: {file_path}")
            docs.extend(TextLoader(file_path).load())
    elif URL:
        print(f"Crawling URL: {URL}")
        loader = UnstructuredURLLoader(urls=[URL])
        docs.extend(loader.load())
    else:
        print("No DOCS_DIR or URL specified.")
        sys.exit(1)
    return docs


def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""],
    )
    chunks = []
    for doc in docs:
        splits = splitter.split_documents([doc])
        chunks.extend(splits)
    print(f"Chunked to {len(chunks)} segments")
    return chunks


def get_openai_embeddings(texts):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)
    return embeddings.embed_documents([chunk.page_content for chunk in texts])


def compute_chunk_hash(text):
    """Compute a hash of chunk text for deduplication."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def store_in_supabase(chunks, vectors):
    url, key = SUPABASE_URL, SUPABASE_KEY
    supabase: Client = create_client(url, key)
    for chunk, vector in zip(chunks, vectors):
        chunk_hash = compute_chunk_hash(chunk.page_content)
        # Query for this hash
        existing = (
            supabase.table(SUPABASE_TABLE)
            .select("id")
            .eq("chunk_hash", chunk_hash)
            .execute()
        )
        if existing.data:
            print(f"Skipping duplicate chunk (hash: {chunk_hash})")
            continue
        print(f"Inserting new chunk (hash: {chunk_hash})")
        data, count = (
            supabase.table(SUPABASE_TABLE)
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
    if not (OPENAI_API_KEY and SUPABASE_URL and SUPABASE_KEY):
        print(
            "Missing environment variables. Required: OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY"
        )
        sys.exit(1)

    # 1. Load documents
    documents = load_documents()

    # 2. Chunk documents
    chunks = chunk_documents(documents)

    # 3. Create embeddings
    embeddings = get_openai_embeddings(chunks)

    # 4. Store results in Supabase
    store_in_supabase(chunks, embeddings)

    print("Done!")
