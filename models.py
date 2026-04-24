from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import UploadFile, File


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="用户输入的文本提示")
    image_url: Optional[str] = Field(None, description="图片URL地址")
    max_new_tokens: Optional[int] = Field(128, description="最大生成token数", ge=1, le=2048)
    temperature: Optional[float] = Field(0.7, description="温度参数", ge=0.0, le=2.0)
    top_p: Optional[float] = Field(0.95, description="top_p采样参数", ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    success: bool
    response: str
    error: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatHistoryRequest(BaseModel):
    messages: List[ChatMessage]
    max_new_tokens: Optional[int] = Field(128, description="最大生成token数", ge=1, le=2048)
    temperature: Optional[float] = Field(0.7, description="温度参数", ge=0.0, le=2.0)
    top_p: Optional[float] = Field(0.95, description="top_p采样参数", ge=0.0, le=1.0)


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str
