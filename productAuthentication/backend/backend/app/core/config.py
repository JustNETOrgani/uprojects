from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Anti-Counterfeit Blockchain API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database settings
    DATABASE_URL: str ="postgresql+psycopg2://postgres.bcabdfgfmxnahtokonvw:S7kBHDlnRMjzicp8@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"# "sqlite:////Users/mac/meta_mask/backend/anticounterfeit.db"

    # Security settings
    SECRET_KEY: str = "secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]

    # Blockchain settings
    ETHEREUM_NETWORK: str = "localhost"  # localhost, sepolia, mainnet
    CONTRACT_ADDRESS: Optional[str] = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    INFURA_URL: Optional[str] = "https://sepolia.infura.io/v3/3fc69367be4b4c69b6eac66940180f94"
    PRIVATE_KEY: Optional[str] = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

    CLOUDINARY_CLOUD_NAME: str = Field(..., env="CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = Field(..., env="CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = Field(..., env="CLOUDINARY_API_SECRET")

    # QR Code settings
    QR_CODE_STORAGE_PATH: str = "./static/qr_codes"  # probably gonna change it

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"

    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"

    # Email settings (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # IPFS settings
    IPFS_GATEWAY: str = "http://127.0.0.1:5001"
    IPFS_PUBLIC_GATEWAY: str = "https://ipfs.io/ipfs/"
    
    # Swarm settings (legacy)
    SWARM_GATEWAY: str = "http://localhost:1633"
    SWARM_PUBLIC_GATEWAY: str = "https://swarm-gateways.net/bzz:/"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

os.makedirs(settings.QR_CODE_STORAGE_PATH, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
