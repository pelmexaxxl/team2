import aiohttp
import asyncpg
from datetime import datetime, timedelta
import logging
from app.configs import settings
import asyncio


logger = logging.getLogger(__name__)
YANDEX_GPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


async def ask_yandex_gpt(prompt: str, model: str = "yandexgpt-lite") -> str:
    """Отправляет запрос к Yandex GPT API и возвращает ответ."""
    logger.info(f"Sending request to Yandex GPT, prompt length: {len(prompt)} chars")
    headers = {
        "Authorization": f"Bearer {settings.yandex_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"gpt://b1gadudlvblk40h9bm6i/yandexgpt",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": 10000
        },
        "messages": [
            {"role": "system", "text": "Ты анализируешь сообщения из командного чата и оцениваешь их тональность."},
            {"role": "user", "text": prompt}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(YANDEX_GPT_API_URL, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"Yandex GPT error: {resp.status} — {error_text}")
                    raise Exception(f"YandexGPT error: {resp.status} — {error_text}")
                data = await resp.json()
                result = data["result"]["alternatives"][0]["message"]["text"]
                logger.info(f"Received response from Yandex GPT, length: {len(result)} chars")
                return result
    except Exception as e:
        logger.error(f"Error in ask_yandex_gpt: {e}", exc_info=True)
        raise


async def ask_chat_messages_gpt(chat_id: int, question: str, hours: int = 24) -> str:
    """
    Отправляет сообщения из чата за указанный период в Яндекс ГПТ с заданным вопросом.
    
    Args:
        chat_id: ID чата
        question: Вопрос для Яндекс ГПТ
        hours: Количество часов, за которые нужно взять сообщения (по умолчанию 24)
    
    Returns:
        Ответ от Яндекс ГПТ
    """
    logger.info(f"Starting ask_chat_messages_gpt for chat {chat_id} with question: {question}")
    
    try:
        conn = await asyncpg.connect(settings.database_url)
        logger.info("Database connection established")
        
        # Получаем сообщения из чата за указанный период
        period_start = datetime.now() - timedelta(hours=hours)
        rows = await conn.fetch("""
            SELECT username, content, created_at
            FROM messages
            WHERE chat_id = $1 AND created_at > $2
            ORDER BY created_at
        """, chat_id, period_start)
        
        await conn.close()
        
        logger.info(f"Found {len(rows)} messages for chat {chat_id} since {period_start}")
        
        if not rows:
            return f"В чате нет сообщений за последние {hours} часов."
        
        # Форматируем сообщения для отправки в Яндекс ГПТ
        messages_text = "\n".join(
            f"[{row['username'] or 'Пользователь'} {row['created_at'].strftime('%H:%M:%S')}] {row['content']}" 
            for row in rows
        )
        
        # Формируем запрос с вопросом пользователя
        prompt = (
            f"Ниже приведены сообщения из чата за последние {hours} часов.\n\n"
            f"{messages_text}\n\n"
            f"Вопрос: {question}"
        )
        
        # Отправляем запрос в Яндекс ГПТ
        logger.info(f"Sending request to Yandex GPT for chat {chat_id}")
        result = await ask_yandex_gpt(prompt)
        
        return result
    except Exception as e:
        logger.error(f"Error in ask_chat_messages_gpt: {e}", exc_info=True)
        return f"Произошла ошибка при обработке запроса: {str(e)}"


async def analyze_chat_messages(chat_id=None):
    """
    Analyze messages from a specific chat or all chats.
    If chat_id is None, analyze all chats with message collection enabled.
    """
    logger.info(f"Starting analyze_chat_messages for chat_id: {chat_id or 'all'}")
    
    try:
        conn = await asyncpg.connect(settings.database_url)
        logger.info("Database connection established")
        yesterday = datetime.now() - timedelta(days=1)
        
        if chat_id:
            # Analyze a specific chat
            logger.info(f"Analyzing chat: {chat_id}")
            await analyze_single_chat(conn, chat_id, yesterday)
            await conn.close()
            return "Готово. Результат анализа сохранён в базе."
        else:
            # Analyze all chats with collection enabled
            logger.info("Analyzing all chats with collection enabled")
            chats = await conn.fetch(
                "SELECT chat_id FROM chat_settings WHERE collect_messages = true"
            )
            
            logger.info(f"Found {len(chats)} chats with collection enabled")
            
            for chat in chats:
                try:
                    await analyze_single_chat(conn, chat['chat_id'], yesterday)
                except Exception as e:
                    logger.error(f"Error analyzing chat {chat['chat_id']}: {e}", exc_info=True)
            
            await conn.close()
            return f"Завершен анализ {len(chats)} чатов."
    except Exception as e:
        logger.error(f"Error in analyze_chat_messages: {e}", exc_info=True)
        return f"Ошибка при анализе: {str(e)}"


async def analyze_single_chat(conn, chat_id, since_date):
    """Analyze messages from a single chat."""
    logger.info(f"Starting analyze_single_chat for chat_id: {chat_id}")
    
    # Получаем сообщения из чата за последние сутки
    rows = await conn.fetch("""
        SELECT username, content
        FROM messages
        WHERE chat_id = $1 AND created_at > $2
        ORDER BY created_at
    """, chat_id, since_date)

    logger.info(f"Found {len(rows)} messages for chat {chat_id} since {since_date}")
    
    if not rows:
        logger.info(f"No messages to analyze for chat {chat_id}")
        return

    # Формируем текст сообщений для анализа
    messages_text = "\n".join(
        f"[{row['username'] or 'Пользователь'}] {row['content']}" for row in rows
    )

    # Формируем запрос для Yandex GPT
    prompt = (
        "Проанализируй следующие сообщения за последние сутки. "
        "Оцени общий тон чата (позитивный/нейтральный/негативный), "
        "укажи долю токсичных сообщений и пользователей с резкими формулировками.\n\n"
        + messages_text
    )

    # Отправляем запрос в Yandex GPT
    logger.info(f"Sending request to Yandex GPT for chat {chat_id}")
    result = await ask_yandex_gpt(prompt)

    # Сохраняем результат анализа в базу данных
    logger.info(f"Saving analysis result for chat {chat_id}")
    await conn.execute("""
        INSERT INTO chat_analytics (chat_id, analyzed_at, result)
        VALUES ($1, NOW(), $2)
    """, chat_id, result)
    
    # Обновляем время последнего анализа
    await conn.execute("""
        UPDATE chat_settings
        SET last_analyzed = NOW()
        WHERE chat_id = $1
    """, chat_id)
    
    logger.info(f"Completed analysis for chat {chat_id}")


async def run_daily_analysis():
    """Run daily analysis of all chat messages at a specific time."""
    logger.info("Started daily analysis scheduler")
    
    while True:
        now = datetime.now()
        # Schedule for 23:00 every day
        target_time = now.replace(hour=23, minute=0, second=0, microsecond=0)
        
        # If we've already passed the target time today, schedule for tomorrow
        if now > target_time:
            target_time = target_time + timedelta(days=1)
            
        # Calculate seconds until target time
        seconds_until_target = (target_time - now).total_seconds()
        logger.info(f"Scheduled next daily analysis in {seconds_until_target} seconds (at {target_time})")
        
        # Wait until the target time
        await asyncio.sleep(seconds_until_target)
        
        # Run the analysis
        try:
            logger.info("Starting daily chat analysis")
            result = await analyze_chat_messages()
            logger.info(f"Daily chat analysis completed: {result}")
        except Exception as e:
            logger.error(f"Error in daily analysis: {e}", exc_info=True)
            
        # Wait a minute before checking the schedule again
        await asyncio.sleep(60)
