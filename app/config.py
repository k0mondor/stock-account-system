from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/account_db"
    
    # JWT配置
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # 应用配置
    DEBUG: bool = True
    APP_TITLE: str = "股票交易系统-账户业务子系统"
    SERVICE_NAME: str = "account-service"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
