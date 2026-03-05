from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/payforwechat?charset=utf8mb4"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    ADMIN_API_KEY: str = ""
    ALLOW_LOCAL_NOTIFY: bool = True
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    PLATFORM_FEE_RATE: float = 0.10

    WECHAT_ENABLED: bool = False
    WECHAT_BASE_URL: str = "https://api.mch.weixin.qq.com"
    WECHAT_MCH_ID: str = ""
    WECHAT_APP_ID: str = ""
    WECHAT_MCH_SERIAL_NO: str = ""
    WECHAT_API_V3_KEY: str = ""
    WECHAT_PRIVATE_KEY_PATH: str = ""
    WECHAT_PRIVATE_KEY_PEM: str = ""
    WECHAT_PLATFORM_CERT_PATH: str = ""
    WECHAT_CALLBACK_STRICT: bool = False
    WECHAT_PAY_NOTIFY_URL: str = ""
    WECHAT_TRANSFER_NOTIFY_URL: str = ""
    WECHAT_TRANSFER_AUTO_APPROVE: bool = False

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
