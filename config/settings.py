from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    db_driver: str
    db_name: str
    db_host: str
    db_port: int
    db_user: str
    db_pass: str

    ml_mode: str
    ml_service_url: str
    allowed_origins: str
    tf_model_path: str
    debug: bool
    allowed_file_types: list[str] = ["image/jpeg", "image/png", "image/webp"]
    max_file_size_mb: int = 10

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()