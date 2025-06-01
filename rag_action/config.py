import os


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
