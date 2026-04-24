import sqlite3

DB_NAME = "tea_bot.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fertilizer_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_stage TEXT,
        soil_condition TEXT,
        fertilizer TEXT,
        recommendation TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS disease_advice (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symptom TEXT,
        disease_name TEXT,
        advice TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS market_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tea_grade TEXT,
        price REAL,
        price_date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS learned_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT,
        bot_response TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def insert_sample_data():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM fertilizer_plans")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO fertilizer_plans 
        (crop_stage, soil_condition, fertilizer, recommendation)
        VALUES (?, ?, ?, ?)
        """, [
            ("young", "normal", "NPK 10-10-10", "Use balanced fertilizer in small quantities for young tea plants."),
            ("mature", "normal", "NPK 20-10-10", "Use nitrogen-rich fertilizer for mature tea bushes after harvesting."),
            ("acidic", "low pH", "Dolomite", "Apply dolomite if soil pH is low, based on soil test results.")
        ])

    cur.execute("SELECT COUNT(*) FROM disease_advice")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO disease_advice
        (symptom, disease_name, advice)
        VALUES (?, ?, ?)
        """, [
            ("brown spots", "Fungal leaf spot", "Remove infected leaves and apply recommended fungicide."),
            ("yellow leaves", "Nutrient deficiency", "Check nitrogen level and soil drainage."),
            ("wilting", "Root disease", "Improve drainage and inspect roots for infection.")
        ])

    cur.execute("SELECT COUNT(*) FROM market_prices")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO market_prices
        (tea_grade, price, price_date)
        VALUES (?, ?, ?)
        """, [
            ("BOPF", 1250.00, "2026-04-24"),
            ("OP", 1180.00, "2026-04-24"),
            ("Dust", 980.00, "2026-04-24")
        ])

    conn.commit()
    conn.close()


def save_chat(user_message, bot_response):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO chat_history (user_message, bot_response)
    VALUES (?, ?)
    """, (user_message, bot_response))
    conn.commit()
    conn.close()


def save_learned_answer(question, answer):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO learned_answers (question, answer)
    VALUES (?, ?)
    """, (question, answer))
    conn.commit()
    conn.close()