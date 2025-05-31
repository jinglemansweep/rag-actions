import os
from dataclasses import dataclass


def get_env_var(var_name: str, default=None, cast_type=str):
    """
    Get an environment variable, with optional default value and type casting.
    """
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set")
    try:
        return cast_type(value)
    except ValueError as e:
        raise ValueError(f"Invalid value for {var_name}: {value}") from e


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


base_config = BaseConfig(
    openai_api_key=get_env_var("OPENAI_API_KEY"),
    supabase_url=get_env_var("SUPABASE_URL"),
    supabase_key=get_env_var("SUPABASE_KEY"),
    supabase_table=get_env_var("SUPABASE_TABLE"),
    embedding_model=get_env_var("EMBEDDING_MODEL", "text-embedding-ada-002"),
)
