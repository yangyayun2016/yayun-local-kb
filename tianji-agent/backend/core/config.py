"""
天机智能体 - 全局配置
"""

from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "天机智能体 TianJi AI Agent"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./tianji.db"  # 默认SQLite，生产环境可切换PostgreSQL
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 向量数据库配置 (Milvus/Pinecone)
    VECTOR_DB_TYPE: str = "milvus"  # 或 "pinecone", "qdrant"
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    VECTOR_DIMENSION: int = 1536  # OpenAI embedding维度
    
    # LLM API 配置
    OPENAI_API_KEY=[已移除] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    ANTHROPIC_API_KEY=[已移除] = None
    
    # 国产大模型
    DEEPSEEK_API_KEY=[已移除] = None
    QWEN_API_KEY=[已移除] = None
    WENXIN_API_KEY=[已移除] = None
    
    # JWT 配置
    SECRET_KEY: str = "tianji-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 积分系统配置
    POINTS_PER_SKILL_PUBLISH: int = 100
    POINTS_PER_SKILL_INSTALL: int = 5
    POINTS_PER_SKILL_USE: int = 1
    POINTS_PER_INVITE: int = 200
    POINTS_PER_DAILY_LOGIN: int = 10
    
    # 文件存储
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # 支持的外部平台
    SUPPORTED_PLATFORMS: List[str] = [
        "amazon", "shopify", "tiktok_shop", "wix", "woocommerce", 
        "ebay", "etsy", "temu", "shein", "alibaba"
    ]
    
    class Config:
        env_file = ".env"


settings = Settings()
