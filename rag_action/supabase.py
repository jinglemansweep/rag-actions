import logging
from supabase import create_client, Client  # type: ignore


logger = logging.getLogger(__name__)


def build_supabase_client(supabase_url: str, supabase_key: str) -> Client:
    """
    Build a Supabase client using the provided URL and key.
    """

    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL and key must be provided")

    return create_client(supabase_url, supabase_key)
