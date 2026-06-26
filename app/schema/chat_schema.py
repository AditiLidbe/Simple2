from datetime import datetime

from pydantic import BaseModel, Field

from ..model.chat_model import ChatRole


class ChatMessageCreate(BaseModel):
    message: str = Field(min_length=1)


class ChatMessageResponse(BaseModel):
    id: int
    sender: ChatRole
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: int
    appointment_id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageResponse] = []

    class Config:
        from_attributes = True
