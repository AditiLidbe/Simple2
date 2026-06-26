from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as PYENUM, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class ChatRole(str, Enum):
    PATIENT = "PATIENT"
    ASSISTANT = "ASSISTANT"
    TOOL = "TOOL"


class ChatSessionModel(Base):
    __tablename__ = "chat_session_model"

    id = Column(Integer, primary_key=True, nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointment_model.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("user_model.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    appointment = relationship("AppointmentModel")
    patient = relationship("UserModel")
    messages = relationship("ChatMessageModel", back_populates="session", cascade="all, delete-orphan")


class ChatMessageModel(Base):
    __tablename__ = "chat_message_model"

    id = Column(Integer, primary_key=True, nullable=False)
    session_id = Column(Integer, ForeignKey("chat_session_model.id"), nullable=False)
    sender = Column(PYENUM(ChatRole), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    session = relationship("ChatSessionModel", back_populates="messages")
