from datetime import datetime

from enum import Enum as PyEnum

from sqlalchemy import Enum as SQLEnum, String, BigInteger, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from .base import Base


class Role(PyEnum):
    ADMIN = 'admin'
    EMPLOYEE = 'employee'
    HR = 'hr'


class User(Base):
    __tablename__ = 'users'
    
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    role: Mapped[Role] = mapped_column(SQLEnum(
        Role, name='user_role_enum'
    ), nullable=True)
    username: Mapped[str] = mapped_column(String(64), nullable=True, unique=True)
    
    answers: Mapped[list["UserAnswer"]] = relationship(back_populates="user")
    results: Mapped[list["SurveyResult"]] = relationship(back_populates="user")


class Question(Base):
    __tablename__ = 'questions'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str] = mapped_column(String(1024), nullable=False)
    options: Mapped[list[str]] = mapped_column(ARRAY(String(1024)), nullable=False)
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id"))
    
    poll: Mapped["Poll"] = relationship(back_populates="questions")


class Poll(Base):
    __tablename__ = "polls"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    
    questions: Mapped[list[Question]] = relationship(back_populates="poll")


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    answer_index: Mapped[int] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship()


class SurveyResult(Base):
    __tablename__ = "survey_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    emotion_score: Mapped[int] = mapped_column()
    emotion_label: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    user: Mapped["User"] = relationship(back_populates="results")
