import aiohttp
import asyncpg
from datetime import datetime, timedelta
from app.configs import settings

YANDEX_GPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

async def ask_yandex_gpt(prompt: str, model: str = "yandexgpt-lite") -> str:
    headers = {
        "Authorization": f"Api-Key {settings.yandex_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"gpt://{model}/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": 500
        },
        "messages": [
            {"role": "system", "text": "Ты анализируешь сообщения из командного чата и оцениваешь их тональность."},
            {"role": "user", "text": prompt}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(YANDEX_GPT_API_URL, headers=headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(f"YandexGPT error: {resp.status} — {await resp.text()}")
            data = await resp.json()
            return data["result"]["alternatives"][0]["message"]["text"]


async def analyze_chat_messages():
    conn = await asyncpg.connect(settings.database_url)
    yesterday = datetime.utcnow() - timedelta(days=1)

    rows = await conn.fetch("""
        SELECT username, content
        FROM messages
        WHERE created_at > $1
        ORDER BY created_at
    """, yesterday)

    if not rows:
        await conn.close()
        return "Нет сообщений за последние сутки."

    messages_text = "\n".join(
        f"[{row['username']}] {row['content']}" for row in rows
    )

    prompt = (
        "Проанализируй следующие сообщения за последние сутки. "
        "Оцени общий тон чата (позитивный/нейтральный/негативный), "
        "укажи долю токсичных сообщений и пользователей с резкими формулировками.\n\n"
        + messages_text
    )

    result = await ask_yandex_gpt(prompt)

    await conn.execute("""
        INSERT INTO chat_analytics (analyzed_at, result)
        VALUES (NOW(), $1)
    """, result)

    await conn.close()
    return "Готово. Результат анализа сохранён в базе."
