import tempfile
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def cache_dir_factory():
    """Cache directory factory method"""
    return Path(tempfile.gettempdir())


class Settings(BaseSettings):
    """Settings model"""
    api_key: str = ''
    cache_dir: Path = Field(default_factory=cache_dir_factory)
    timeout: float | None = None
    model_config = SettingsConfigDict(env_prefix='todoist_', env_file='.env', env_file_encoding='utf-8', extra='ignore')
