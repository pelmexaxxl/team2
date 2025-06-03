# app/models/extras.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class ChatSettings(Base):
    __tablename__ = "chat_settings"
    chat_id = Column(Integer, primary_key=True)
    welcome_text = Column(String, default=None)          # 1
    collect_messages = Column(Boolean, default=False)

class PollTemplate(Base):
    __tablename__ = "poll_templates"                     # 4
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.tg_id"))
    json_body = Column(String)     # сериализованный список вопросов

class Reminder(Base):
    __tablename__ = "poll_reminders"                     # 5
    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey("polls.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_done = Column(Boolean, default=False)
