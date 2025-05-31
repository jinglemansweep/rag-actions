import os
from dataclasses import dataclass

required_env_vars = [
    "ACTION_MODE",
    "OPENAI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_KEY",
]

missing_vars = []
for env_var in required_env_vars:
    if not os.getenv(env_var):
        missing_vars.append(env_var)
if len(missing_vars) > 0:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing_vars)}"
    )


@dataclass
class Config:
    """Configuration for RAG Action."""

    action_mode: str
    openai_api_key: str
    embedding_model: str
    supabase_url: str
    supabase_key: str
    supabase_table: str
    chunk_size: int
    chunk_overlap: int
    ingest_dir: str
    ingest_pattern: str
    ingest_text: str
    ingest_metadata: str
    query_text: str
    query_top_k: int


settings = Config(
    action_mode=os.getenv("ACTION_MODE", "ingest"),
    openai_api_key=os.getenv("OPENAI_API_KEY", ""),
    embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002"),
    supabase_url=os.getenv("SUPABASE_URL", ""),
    supabase_key=os.getenv("SUPABASE_KEY", ""),
    supabase_table=os.getenv("SUPABASE_TABLE", "documents"),
    chunk_size=int(os.getenv("CHUNK_SIZE", "500")),
    chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
    ingest_dir=os.getenv("INGEST_DIR", ""),
    ingest_pattern=os.getenv("INGEST_PATTERN", "*.*"),
    ingest_text=os.getenv("INGEST_TEXT", ""),
    ingest_metadata=os.getenv("INGEST_METADATA", "{}"),
    query_text=os.getenv("QUERY_TEXT", ""),
    query_top_k=int(os.getenv("QUERY_TOP_K", "5")),
)
