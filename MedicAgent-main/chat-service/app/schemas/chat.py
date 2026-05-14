from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class NLURequest(BaseModel):
    text: str
    lang: str = "vi"


class OrchestrateRequest(BaseModel):
    text: str
    lang: str = "vi"


class SendMessage(BaseModel):
    role: str = Field(..., pattern="^(user|system)$")
    content: str
    attachments: Optional[list[dict]] = None
    stream: Optional[bool] = True
    options: Optional[Dict[str, Any]] = None


class SendAck(BaseModel):
    conversation_id: str
    session_id: str
    message_id: str
    stream_url: str

