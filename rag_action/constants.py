from dataclasses import dataclass


@dataclass
class BaseConfig:
    """
    Base Configuration
    """

    openai_api_key: str
    supabase_url: str
    supabase_key: str
    supabase_table: str
    embedding_model: str
