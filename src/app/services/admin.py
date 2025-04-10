from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Poll, Question


async def create_poll(session: AsyncSession, title: str, creator_id: int) -> int:
    poll = Poll(title=title)
    session.add(poll)
    await session.flush()  # чтобы получить poll.id
    return poll.id


# Функция добавления вопроса к опросу
async def add_question_to_poll(session: AsyncSession, poll_id: int, text: str, options: list[str]) -> int:
    question = Question(poll_id=poll_id, text=text, options=options)
    session.add(question)
    await session.flush()  # чтобы получить question.id
    return question.id