import random
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from train_data import TRAINING_DATA
from database import DB_NAME, save_chat, save_learned_answer


questions = [item[0] for item in TRAINING_DATA]
intents = [item[1] for item in TRAINING_DATA]

vectorizer = TfidfVectorizer()
question_vectors = vectorizer.fit_transform(questions)


def get_db_connection():
    return sqlite3.connect(DB_NAME)


def detect_intent(user_message):
    user_vector = vectorizer.transform([user_message.lower()])
    similarity = cosine_similarity(user_vector, question_vectors)

    best_index = similarity.argmax()
    best_score = similarity[0][best_index]

    if best_score < 0.25:
        return "unknown", best_score

    return intents[best_index], best_score


def get_fertilizer_answer():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT crop_stage, fertilizer, recommendation FROM fertilizer_plans")
    rows = cur.fetchall()
    conn.close()

    answer = "Fertilizer recommendations:\n"
    for row in rows:
        answer += f"- Stage: {row[0]}, Fertilizer: {row[1]}, Advice: {row[2]}\n"

    return answer


def get_disease_answer(user_message):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT symptom, disease_name, advice FROM disease_advice")
    rows = cur.fetchall()
    conn.close()

    for symptom, disease, advice in rows:
        if symptom.lower() in user_message.lower():
            return f"Possible issue: {disease}. Advice: {advice}"

    return "Tea disease advice: inspect leaf color, spots, wilting, and drainage. Brown spots may indicate fungal disease."


def get_market_price_answer():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT tea_grade, price, price_date FROM market_prices")
    rows = cur.fetchall()
    conn.close()

    answer = "Current tea market prices:\n"
    for grade, price, date in rows:
        answer += f"- {grade}: Rs. {price} per kg on {date}\n"

    return answer


def search_learned_answers(user_message):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT question, answer FROM learned_answers")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    learned_questions = [row[0] for row in rows]
    learned_answers = [row[1] for row in rows]

    learned_vectorizer = TfidfVectorizer()
    learned_vectors = learned_vectorizer.fit_transform(learned_questions)

    user_vector = learned_vectorizer.transform([user_message])
    similarity = cosine_similarity(user_vector, learned_vectors)

    best_index = similarity.argmax()
    best_score = similarity[0][best_index]

    if best_score >= 0.30:
        return learned_answers[best_index]

    return None


def get_bot_response(user_message):
    intent, score = detect_intent(user_message)

    if intent == "greeting":
        response = random.choice([
            "Hello! I am your Tea Farmer Assistant Bot.",
            "Good day! How can I help with your tea farming today?"
        ])

    elif intent == "thanks":
        response = random.choice([
            "You are welcome.",
            "Happy to help your tea farming work."
        ])

    elif intent == "bye":
        response = "Goodbye. I wish you a healthy tea harvest."

    elif intent == "fertilizer":
        response = get_fertilizer_answer()

    elif intent == "disease":
        response = get_disease_answer(user_message)

    elif intent == "market_price":
        response = get_market_price_answer()

    elif intent == "weather":
        response = "Weather advice: avoid applying fertilizer before heavy rain. Good drainage is important for tea plants."

    else:
        learned = search_learned_answers(user_message)

        if learned:
            response = learned
        else:
            response = "I do not know the answer yet. Please teach me using: teach: your answer"

    save_chat(user_message, response)
    return response


def teach_bot(question, answer):
    save_learned_answer(question, answer)
    return "Thank you. I have learned this new tea farming knowledge."