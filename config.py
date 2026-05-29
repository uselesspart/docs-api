from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    s3_bucket_name: str
    s3_access_key: str
    s3_secret_key: str
    s3_endpoint_url: str = "https://s3.twcstorage.ru"
    s3_region: str = "ru-1"
    s3_public_url: str = ""
    database_url: str = "sqlite:///./files.db"
    api_key: str

    class Config:
        env_file = ".env"

    @property
    def public_base_url(self) -> str:
        """Базовый URL для публичного доступа к файлам."""
        if self.s3_public_url:
            return self.s3_public_url
        return f"{self.s3_endpoint_url}/{self.s3_bucket_name}"


settings = Settings()