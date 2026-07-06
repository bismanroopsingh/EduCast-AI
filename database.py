import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


# ==========================================
# Connect to Database
# ==========================================

def connect_db():

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT"))
    )

    cursor = connection.cursor(dictionary=True)

    return connection, cursor


# ==========================================
# Close Connection
# ==========================================

def close_db(connection, cursor):

    cursor.close()
    connection.close()


# ==========================================
# Create / Get User
# ==========================================

def create_user(username, email=None):

    connection, cursor = connect_db()

    cursor.execute(
        """
        SELECT user_id
        FROM users
        WHERE username=%s
        """,
        (username,)
    )

    existing = cursor.fetchone()

    if existing:

        user_id = existing["user_id"]

        close_db(connection, cursor)

        return user_id

    cursor.execute(
        """
        INSERT INTO users(username,email)
        VALUES(%s,%s)
        """,
        (username, email)
    )

    connection.commit()

    user_id = cursor.lastrowid

    close_db(connection, cursor)

    return user_id


# ==========================================
# Save Uploaded Document
# ==========================================

def save_document(user_id, filename, content):

    connection, cursor = connect_db()

    cursor.execute(
        """
        INSERT INTO documents
        (user_id, file_name, content)
        VALUES (%s,%s,%s)
        """,
        (
            user_id,
            filename,
            content
        )
    )

    connection.commit()

    document_id = cursor.lastrowid

    close_db(connection, cursor)

    return document_id

# ==========================================
# Save Lesson
# ==========================================

def save_lesson(document_id, topic, lesson_text):

    connection, cursor = connect_db()

    cursor.execute(
        """
        INSERT INTO lessons(document_id,topic,lesson_text)
        VALUES(%s,%s,%s)
        """,
        (
            document_id,
            topic,
            lesson_text
        )
    )

    connection.commit()

    lesson_id = cursor.lastrowid

    close_db(connection, cursor)

    return lesson_id


# ==========================================
# Save Quiz Attempt
# ==========================================

def save_quiz_attempt(

    user_id,
    lesson_id,
    score,
    total_questions,
    percentage

):

    connection, cursor = connect_db()

    cursor.execute(
        """
        INSERT INTO quiz_attempts
        (
            user_id,
            lesson_id,
            score,
            total_questions,
            percentage
        )
        VALUES(%s,%s,%s,%s,%s)
        """,
        (
            user_id,
            lesson_id,
            score,
            total_questions,
            percentage
        )
    )

    connection.commit()

    close_db(connection, cursor)


# ==========================================
# Save Weak Topic
# ==========================================

def save_weak_topic(

    user_id,
    lesson_id,
    topic,
    weakness_score

):

    connection, cursor = connect_db()

    cursor.execute(
        """
        INSERT INTO weak_topics
        (
            user_id,
            lesson_id,
            topic,
            weakness_score
        )
        VALUES(%s,%s,%s,%s)
        """,
        (
            user_id,
            lesson_id,
            topic,
            weakness_score
        )
    )

    connection.commit()

    close_db(connection, cursor)


# ==========================================
# User Progress
# ==========================================

def get_user_progress(user_id):

    connection, cursor = connect_db()

    cursor.execute(
        """
        SELECT *
        FROM quiz_attempts
        WHERE user_id=%s
        """,
        (user_id,)
    )

    progress = cursor.fetchall()

    close_db(connection, cursor)

    return progress


# ==========================================
# Weak Topics
# ==========================================

def get_weak_topics(user_id):

    connection, cursor = connect_db()

    cursor.execute(
        """
        SELECT *
        FROM weak_topics
        WHERE user_id=%s
        """,
        (user_id,)
    )

    weak_topics = cursor.fetchall()

    close_db(connection, cursor)

    return weak_topics


# ==========================================
# Quiz History
# ==========================================

def get_quiz_history(user_id):

    connection, cursor = connect_db()

    cursor.execute(
        """
        SELECT *
        FROM quiz_attempts
        WHERE user_id=%s
        ORDER BY attempt_date DESC
        """,
        (user_id,)
    )

    history = cursor.fetchall()

    close_db(connection, cursor)

    return history


# ==========================================
# Get Lessons
# ==========================================

def get_lessons(document_id):

    connection, cursor = connect_db()

    cursor.execute(
        """
        SELECT *
        FROM lessons
        WHERE document_id=%s
        """,
        (document_id,)
    )

    lessons = cursor.fetchall()

    close_db(connection, cursor)

    return lessons


# ==========================================
# Get Documents
# ==========================================

def get_documents(user_id):

    connection, cursor = connect_db()

    cursor.execute(
        """
        SELECT *
        FROM documents
        WHERE user_id=%s
        """
        ,
        (user_id,)
    )

    documents = cursor.fetchall()

    close_db(connection, cursor)

    return documents
