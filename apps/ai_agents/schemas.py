from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Literal

# ==========================================
# Agent Types (Updated)
# ==========================================
AgentType = Literal["financial", "support", "admin", "research", "data_analyst", "code_assistant"]

# ==========================================
# Message Schemas
# ==========================================
class MessageResponse(BaseModel):
    """اسکیمای پاسخ پیام."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    role: Literal["user", "assistant", "tool"]
    content: str
    tool_calls: Optional[dict] = None
    tool_call_id: Optional[str] = None
    created_at: datetime

# ==========================================
# Conversation Schemas
# ==========================================
class ConversationCreate(BaseModel):
    """اسکیمای ایجاد مکالمه."""
    agent_type: AgentType
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    """اسکیمای پاسخ مکالمه."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    agent_type: AgentType
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

class ConversationDetail(ConversationResponse):
    """پاسخ مکالمه با تمام پیام‌ها."""
    messages: List[MessageResponse] = []

# ==========================================
# Chat Schemas
# ==========================================
class ChatRequest(BaseModel):
    """درخواست چت (پیام جدید)."""
    conversation_id: Optional[int] = Field(None, description="ID مکالمه موجود. اگر None باشد، مکالمه جدید ایجاد می‌شود.")
    message: str = Field(..., min_length=1, max_length=4000)
    agent_type: AgentType = "financial"

class ChatResponse(BaseModel):
    """پاسخ چت."""
    conversation_id: int
    assistant_message: str
    messages: List[MessageResponse]