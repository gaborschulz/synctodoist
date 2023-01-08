import tempfile
from pathlib import Path

from pydantic import BaseSettings, Field


def cache_dir_factory():
    """Cache directory factory method"""
    return Path(tempfile.gettempdir())


class Settings(BaseSettings):
    """Settings model"""
    api_key: str = ''
    cache_dir: Path = Field(default_factory=cache_dir_factory)

    class Config:
        """Settings configuration"""
        env_prefix = 'todoist_'
        env_file = '.env'
        env_file_encoding = 'utf-8'
