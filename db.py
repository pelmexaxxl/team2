import psycopg2
from config import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_poll(title, description, creator_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO polls (title, description, creator_id)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (title, description, creator_id))
    poll_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return poll_id

def add_question_to_poll(poll_id, text, is_open):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO questions (poll_id, text, is_open)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (poll_id, text, is_open))
    q_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return q_id

def add_option_to_question(question_id, text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO options (question_id, text)
        VALUES (%s, %s)
    """, (question_id, text))
    conn.commit()
    cur.close()
    conn.close()


def get_users_in_chat(chat_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id FROM users u
        JOIN chat_members cm ON cm.user_id = u.id
        WHERE cm.chat_id = %s
    """, (chat_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return [{'id': row[0]} for row in result]