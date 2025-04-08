-- Пользователи
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Беседы (группы)
CREATE TABLE chats (
    id BIGINT PRIMARY KEY,
    title TEXT
);

-- Привязка пользователей к группам
CREATE TABLE chat_members (
    chat_id BIGINT REFERENCES chats(id),
    user_id BIGINT REFERENCES users(id),
    PRIMARY KEY (chat_id, user_id)
);

-- Опросы
CREATE TABLE polls (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    creator_id BIGINT REFERENCES users(id),
    chat_id BIGINT REFERENCES chats(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Вопросы
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    poll_id INTEGER REFERENCES polls(id),
    text TEXT,
    is_open BOOLEAN DEFAULT FALSE -- если TRUE — открытый ответ, если FALSE — варианты
);

-- Варианты ответов
CREATE TABLE options (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES questions(id),
    text TEXT
);

-- Ответы пользователей
CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    question_id INTEGER REFERENCES questions(id),
    option_id INTEGER REFERENCES options(id),
    open_text TEXT
);
