from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "stock-account-backend"
    app_env: str = "development"
    api_prefix: str = "/api/v1/account"
    database_url: str = "mysql+pymysql://root:_Xwz20061005@127.0.0.1:3306/stock_account_db?charset=utf8mb4"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
