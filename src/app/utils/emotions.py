# emotions.py
EMOTION_THRESHOLDS = {
    "depressed": (0, 6),
    "neutral": (7, 12),
    "positive": (13, 18)
}

def calculate_emotion(answers: list[int]) -> dict:
    total_score = sum(answers)
    
    for emotion, (min_score, max_score) in EMOTION_THRESHOLDS.items():
        if min_score <= total_score <= max_score:
            return {
                "score": total_score,
                "label": emotion,
                "description": get_emotion_description(emotion)
            }

def get_emotion_description(label: str) -> str:
    descriptions = {
        "depressed": "Ваше состояние требует внимания. Рекомендуем обратиться к специалисту.",
        "neutral": "Ваше состояние стабильно. Не забывайте заботиться о себе.",
        "positive": "Отличные показатели! Продолжайте в том же духе!"
    }
    return descriptions.get(label, "Не удалось определить состояние")


from aiogram import Bot, types
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

async def setup_bot_commands(bot: Bot):
    # Основные команды для всех пользователей
    basic_commands = [
        BotCommand(command="start", description="🎉 Регистрация и приветствие"),
        BotCommand(command="help", description="ℹ️ Справка и список команд"),
        BotCommand(command="get_chat_id", description="📌 Получить ID текущего чата"),

    # Команды для HR и Admin в личных сообщениях
        BotCommand(command="analyze_result", description="📊 Результат анализа чата (указать ID)"),
        BotCommand(command="create_poll", description="🛠️ Создать опрос"),
        BotCommand(command="save_template", description="💾 Сохранить черновик как шаблон"),
        BotCommand(command="use_template", description="🗂️ Загрузить шаблон опроса по ID"),
        BotCommand(command="send_poll", description="📬 Разослать опрос сотрудникам"),
        BotCommand(command="results", description="📋 Сводка по последнему опросу"),
        BotCommand(command="chart_results", description="📊 Диаграмма итогов опроса"),
        BotCommand(command="analis", description="🧠 Сводка состояния сотрудников"),

    # Команды для групп (HR/Admin)
        BotCommand(command="start_collecting", description="📝 Включить сбор сообщений"),
        BotCommand(command="stop_collecting", description="🚫 Выключить сбор сообщений"),
        BotCommand(command="set_welcome", description="👋 Установить приветствие"),

    # Команды для всех в группах
        BotCommand(command="analyze_chat", description="📊 Анализ чата за 24ч"),
        BotCommand(command="ask_chat_gpt", description="🤖 Вопрос GPT по сообщениям"),
    ]

    # Устанавливаем команды по умолчанию (для всех)
    await bot.set_my_commands(basic_commands, scope=BotCommandScopeDefault())

    # Устанавливаем команды для HR/Admin в личных чатах
    # Нужно получить всех HR/Admin и для каждого установить команды
    # Пример для одного пользователя (в реальности нужно циклом для всех)
