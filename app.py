from flask import Flask, render_template, request, jsonify
from database import create_tables, insert_sample_data
from inference_engine import get_bot_response, teach_bot

app = Flask(__name__)

last_unknown_question = None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    global last_unknown_question

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter a message."})

    if user_message.lower().startswith("teach:"):
        answer = user_message.replace("teach:", "", 1).strip()

        if last_unknown_question:
            response = teach_bot(last_unknown_question, answer)
            last_unknown_question = None
        else:
            response = "There is no unknown question to teach."

        return jsonify({"response": response})

    response = get_bot_response(user_message)

    if "I do not know the answer yet" in response:
        last_unknown_question = user_message

    return jsonify({"response": response})


if __name__ == "__main__":
    create_tables()
    insert_sample_data()
    app.run(debug=True)