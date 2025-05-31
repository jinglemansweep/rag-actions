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
    content_dir: str
    content_text: str


settings = Config(
    action_mode=os.getenv("ACTION_MODE", ""),
    openai_api_key=os.getenv("OPENAI_API_KEY", ""),
    embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002"),
    supabase_url=os.getenv("SUPABASE_URL", ""),
    supabase_key=os.getenv("SUPABASE_KEY", ""),
    supabase_table=os.getenv("SUPABASE_TABLE", "rag_chunks"),
    chunk_size=int(os.getenv("CHUNK_SIZE", "500")),
    chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
    content_dir=os.getenv("CONTENT_DIR", ""),
    content_text=os.getenv("CONTENT_TEXT", ""),
)
