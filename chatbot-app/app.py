from flask import Flask, request, jsonify, render_template
import cohere
import os

app = Flask(__name__)
co = cohere.Client(os.environ.get("COHERE_API_KEY"))

history = []

@app.route("/", methods=["GET", "POST"])
def chatbot():
    global history

    if request.method == "POST":
        data = request.get_json()
        personality = data["personality"]
        temperature = float(data["temperature"])
        user_input = data["user_input"]

        if not any(m["role"] == "personality" for m in history):
            history.append({"role": "personality", "content": personality})

        history.append({"role": "user", "content": user_input})

        prompt = ""
        for msg in history:
            if msg["role"] == "personality":
                prompt += msg["content"] + "\n"
            elif msg["role"] in ["user", "bot"]:
                prompt += f"{msg['role']}: {msg['content']}\n"
        prompt += "bot:"

        response = co.generate(
            model="command-light",
            prompt=prompt,
            max_tokens=100,
            temperature=temperature
        )
        bot_reply = response.generations[0].text.strip()
        history.append({"role": "bot", "content": bot_reply})

        visible = [m for m in history if m["role"] != "personality"]
        return jsonify({"history": visible})

    visible = [m for m in history if m["role"] != "personality"]
    return render_template("index.html", history=visible, personality="", temperature=0.5)

@app.route("/reset", methods=["POST"])
def reset_chat():
    global history
    history = []
    return jsonify({"status": "reset", "message": "Chat history cleared."})
