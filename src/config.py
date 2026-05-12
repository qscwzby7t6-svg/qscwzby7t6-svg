"""
项目配置管理模块
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础路径
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    AUDIO_DIR: Path = DATA_DIR / "audio"
    MODELS_DIR: Path = DATA_DIR / "models"
    DB_DIR: Path = DATA_DIR / "db"
    STATIC_DIR: Path = BASE_DIR / "static"
    
    # 数据库配置
    DATABASE_URL: str = f"sqlite:///{DB_DIR}/app.db"
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # 音频处理配置
    SAMPLE_RATE: int = 22050
    MAX_AUDIO_DURATION: int = 300  # 5分钟
    AUDIO_SAMPLE_DURATION: int = 30  # 30秒样本
    
    # AI模型配置
    DEVICE: str = "cuda"  # 可选 'cuda' 或 'cpu'
    STYLE_EMBEDDING_DIM: int = 128
    
    # 版权检测配置
    ORIGINALITY_THRESHOLD: float = 0.7
    SIMILARITY_THRESHOLD: float = 0.3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


# 创建全局配置实例
settings = Settings()

# 确保目录存在
for directory in [
    settings.DATA_DIR,
    settings.AUDIO_DIR,
    settings.MODELS_DIR,
    settings.DB_DIR,
    settings.STATIC_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)
