from __future__ import annotations

from typing import Any, Optional
from urllib.parse import quote_plus

from pydantic import AliasChoices, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
    )

    DB_USER: str = Field(
        validation_alias=AliasChoices("DB_USER", "MYSQL_USER")
    )
    DB_PASSWORD: str = Field(
        validation_alias=AliasChoices("DB_PASSWORD", "MYSQL_PASSWORD")
    )
    DB_HOST: str = Field(
        validation_alias=AliasChoices("DB_HOST", "MYSQL_HOST", "MYSQL_HOSTNAME")
    )
    DB_PORT: int = Field(
        validation_alias=AliasChoices("DB_PORT", "MYSQL_PORT")
    )
    DIRECTORY_DB_NAME: str = Field(
        validation_alias=AliasChoices(
            "DIRECTORY_DB_NAME",
            "DB_NAME",
            "MYSQL_DATABASE",
        )
    )
    QUEUE_DB_NAME: str = Field(
        validation_alias=AliasChoices(
            "QUEUE_DB_NAME",
            "MYSQL_QUEUE_DATABASE",
            "QUEUE_DATABASE_NAME",
        )
    )

    DIRECTORY_DATABASE_URL: Optional[str] = None
    QUEUE_DATABASE_URL: Optional[str] = None

    QDRANT_HOST: str = Field(default="localhost")
    QDRANT_PORT: int = Field(default=6333)
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = Field(default="info_lookup")
    QDRANT_ENABLED: bool = Field(default=True)

    EMBEDDING_MODEL_NAME: str = Field(
        # default="AITeamVN/Vietnamese_Embedding"
        default="AITeamVN/Vietnamese_Embedding"
        
    )
    INFO_LOOKUP_LEXICAL_WEIGHT: float = Field(default=0.01)
    INFO_LOOKUP_SEMANTIC_WEIGHT: float = Field(default=0.99)

    @validator("DIRECTORY_DATABASE_URL", pre=True)
    def assemble_directory_db_connection(
        cls, v: Optional[str], values: dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v

        encoded_password = quote_plus(values["DB_PASSWORD"])

        return (
            f"mysql+pymysql://{values['DB_USER']}:{encoded_password}"
            f"@{values['DB_HOST']}:{values['DB_PORT']}/{values['DIRECTORY_DB_NAME']}"
        )

    @validator("QUEUE_DATABASE_URL", pre=True)
    def assemble_queue_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v

        encoded_password = quote_plus(values["DB_PASSWORD"])

        return (
            f"mysql+pymysql://{values['DB_USER']}:{encoded_password}"
            f"@{values['DB_HOST']}:{values['DB_PORT']}/{values['QUEUE_DB_NAME']}"
        )


settings = Settings()