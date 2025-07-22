from flask import Flask, request, jsonify, render_template
import cohere, os

app = Flask(__name__)
co = cohere.Client(os.environ.get("COHERE_API_KEY"))

history = []  # your in-memory history buffer

@app.route("/", methods=["GET", "POST"])
def chatbot():
    global history

    if request.method == "POST":
        data = request.get_json()
        personality = data["personality"]
        temperature = float(data["temperature"])
        user_input = data["user_input"]

        # Always set personality in history first
        history = [{"role": "personality", "content": personality}]

        # Add user and bot messages
        history.append({"role": "user", "content": user_input})

        prompt = personality + "\n"
        prompt += "\n".join(f"{m['role']}: {m['content']}" for m in history if m["role"] in ["user", "bot"])
        prompt += "\nbot:"

        response = co.generate(
            model="command-light",
            prompt=prompt,
            max_tokens=100,
            temperature=temperature
        )
        bot_reply = response.generations[0].text.strip()
        history.append({"role": "bot", "content": bot_reply})

        # Remove personality before returning to frontend
        visible = [m for m in history if m["role"] != "personality"]
        return jsonify({"history": visible})

    # For GET requests, render without personality visible
    visible = [m for m in history if m["role"] != "personality"]
    return render_template(
        "index.html",
        history=visible,
        personality="",
        temperature=0.5
    )
