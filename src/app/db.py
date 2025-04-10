# import psycopg2
# from psycopg2.extras import DictCursor
# from config import DB_CONFIG

# conn = psycopg2.connect(**DB_CONFIG)

# def get_poll(poll_id):
#     with conn.cursor(cursor_factory=DictCursor) as cur:
#         cur.execute("SELECT * FROM polls WHERE id = %s", (poll_id,))
#         return cur.fetchone()

# def get_questions(poll_id):
#     with conn.cursor(cursor_factory=DictCursor) as cur:
#         cur.execute("SELECT * FROM questions WHERE poll_id = %s ORDER BY id", (poll_id,))
#         return cur.fetchall()

# def get_options(question_id):
#     with conn.cursor(cursor_factory=DictCursor) as cur:
#         cur.execute("SELECT * FROM options WHERE question_id = %s ORDER BY id", (question_id,))
#         return cur.fetchall()

# def save_answer(user_id, question_id, text):
#     with conn.cursor() as cur:
#         cur.execute(
#             "INSERT INTO answers (user_id, question_id, text) VALUES (%s, %s, %s)",
#             (user_id, question_id, text)
#         )
#         conn.commit()