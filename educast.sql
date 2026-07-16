USE educast_ai;

-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS weak_topics;
DROP TABLE IF EXISTS quiz_attempts;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

--------------------------------------------------
-- USERS
--------------------------------------------------

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- DOCUMENTS
--------------------------------------------------

CREATE TABLE documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

--------------------------------------------------
-- LESSONS
--------------------------------------------------

CREATE TABLE lessons (
    lesson_id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    topic VARCHAR(255) NOT NULL,
    lesson_text LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (document_id)
        REFERENCES documents(document_id)
        ON DELETE CASCADE
);

--------------------------------------------------
-- QUIZ ATTEMPTS
--------------------------------------------------

CREATE TABLE quiz_attempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    lesson_id INT NOT NULL,

    score INT NOT NULL,
    total_questions INT NOT NULL,
    percentage FLOAT NOT NULL,

    attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    FOREIGN KEY (lesson_id)
        REFERENCES lessons(lesson_id)
        ON DELETE CASCADE
);

--------------------------------------------------
-- WEAK TOPICS
--------------------------------------------------

CREATE TABLE weak_topics (
    weak_topic_id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,
    lesson_id INT NOT NULL,

    topic VARCHAR(255) NOT NULL,
    weakness_score FLOAT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    FOREIGN KEY (lesson_id)
        REFERENCES lessons(lesson_id)
        ON DELETE CASCADE
);

--------------------------------------------------
-- Verify tables
--------------------------------------------------

SHOW TABLES;

DESCRIBE users;
DESCRIBE documents;
DESCRIBE lessons;
DESCRIBE quiz_attempts;
DESCRIBE weak_topics;

SELECT * FROM users;

SELECT * FROM documents;

SELECT * FROM lessons;

SELECT * FROM quiz_attempts;

SELECT * FROM weak_topics;