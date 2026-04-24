import os
from typing import Optional


class Config:
    MODEL_PATH: str = os.getenv("MODEL_PATH", "C:/llm/Qwen/Qwen3-VL-4B-Instruct")
    DEVICE: str = os.getenv("DEVICE", "cuda:0")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "9000"))
    
    MAX_NEW_TOKENS: int = 128
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.95
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    API_KEY: Optional[str] = os.getenv("API_KEY", None)
    RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", "10000"))


config = Config()
