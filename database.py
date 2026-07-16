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

def get_document_count(user_id):

    connection, cursor = connect_db()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM documents
        WHERE user_id=%s
    """,(user_id,))

    result = cursor.fetchone()

    close_db(connection,cursor)

    return result["total"]

def get_lesson_count(user_id):

    connection,cursor = connect_db()

    cursor.execute("""

        SELECT COUNT(*) AS total

        FROM lessons l

        JOIN documents d

        ON l.document_id=d.document_id

        WHERE d.user_id=%s

    """,(user_id,))

    result=cursor.fetchone()

    close_db(connection,cursor)

    return result["total"]
def get_quiz_count(user_id):

    connection,cursor=connect_db()

    cursor.execute("""

        SELECT COUNT(*) AS total

        FROM quiz_attempts

        WHERE user_id=%s

    """,(user_id,))

    result=cursor.fetchone()

    close_db(connection,cursor)

    return result["total"]
def get_average_score(user_id):

    connection,cursor=connect_db()

    cursor.execute("""

        SELECT AVG(percentage) AS avg_score

        FROM quiz_attempts

        WHERE user_id=%s

    """,(user_id,))

    result=cursor.fetchone()

    close_db(connection,cursor)

    return round(result["avg_score"] or 0,2)

def get_weak_topic_count(user_id):

    connection,cursor=connect_db()

    cursor.execute("""

        SELECT COUNT(*) AS total

        FROM weak_topics

        WHERE user_id=%s

    """,(user_id,))

    result=cursor.fetchone()

    close_db(connection,cursor)

    return result["total"]
def get_all_lessons(user_id):

    connection, cursor = connect_db()

    cursor.execute(
        """
        SELECT
            lessons.topic
        FROM lessons

        JOIN documents
        ON lessons.document_id = documents.document_id

        WHERE documents.user_id=%s
        """,
        (user_id,)
    )

    lessons = cursor.fetchall()

    close_db(connection, cursor)

    return lessons
# ==========================================
# Dashboard Statistics
# ==========================================

def get_dashboard_stats(user_id):

    return {
        "documents": get_document_count(user_id),
        "lessons": get_lesson_count(user_id),
        "quizzes": get_quiz_count(user_id),
        "average_score": get_average_score(user_id),
        "weak_topics": get_weak_topic_count(user_id)
    }
# ==========================================
# Quiz Score History
# ==========================================

def get_quiz_scores(user_id):

    connection, cursor = connect_db()

    cursor.execute("""
        SELECT
            attempt_date,
            percentage
        FROM quiz_attempts
        WHERE user_id=%s
        ORDER BY attempt_date
    """,(user_id,))

    results = cursor.fetchall()

    close_db(connection,cursor)

    return results
# ==========================================
# Top Weak Topics
# ==========================================

def get_top_weak_topics(user_id):

    connection, cursor = connect_db()

    cursor.execute("""
        SELECT
            topic,
            COUNT(*) AS frequency
        FROM weak_topics
        WHERE user_id=%s
        GROUP BY topic
        ORDER BY frequency DESC
        LIMIT 10
    """,(user_id,))

    results = cursor.fetchall()

    close_db(connection,cursor)

    return results
# ==========================================
# Recent Documents
# ==========================================

def get_recent_documents(user_id):

    connection, cursor = connect_db()

    cursor.execute("""
        SELECT
            file_name,
            upload_date
        FROM documents
        WHERE user_id=%s
        ORDER BY upload_date DESC
        LIMIT 5
    """,(user_id,))

    results = cursor.fetchall()

    close_db(connection,cursor)

    return results
# ==========================================
# Study Recommendations
# ==========================================

def get_recommended_topics(user_id):

    connection, cursor = connect_db()

    cursor.execute("""
        SELECT DISTINCT topic
        FROM weak_topics
        WHERE user_id=%s
        ORDER BY weakness_score DESC
        LIMIT 5
    """,(user_id,))

    results = cursor.fetchall()

    close_db(connection,cursor)

    return results
