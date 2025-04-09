CREATE TABLE polls (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    creator_id BIGINT
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    poll_id INTEGER REFERENCES polls(id),
    text TEXT,
    is_open BOOLEAN
);

CREATE TABLE options (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES questions(id),
    text TEXT
);

CREATE TABLE users (
    id BIGINT PRIMARY KEY
);

CREATE TABLE chat_members (
    chat_id BIGINT,
    user_id BIGINT REFERENCES users(id)
);
CREATE TABLE answers (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    question_id INTEGER REFERENCES questions(id),
    text TEXT,                     -- ответ (или выбранный вариант)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
