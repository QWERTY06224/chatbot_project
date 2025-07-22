from flask import Flask, request, jsonify, render_template
import cohere, os

app = Flask(__name__)
co = cohere.Client(os.environ.get("COHERE_API_KEY"))

# In-memory chat history
history = []

@app.route('/', methods=['GET', 'POST'])
def chatbot():
    global history

    if request.method == 'POST':
        data = request.get_json()
        personality = data['personality']
        temp = float(data['temperature'])
        user_input = data['user_input']

        history = [{"role": "personality", "content": personality}] + history
        history.append({"role": "user", "content": user_input})

        prompt = personality.strip() + "\n"
        for msg in history:
            if msg['role'] in ('user', 'bot'):
                prompt += f"{msg['role']}: {msg['content']}\n"
        prompt += "bot:"

        response = co.generate(
            model='command-light',
            prompt=prompt,
            max_tokens=100,
            temperature=temp
        )
        bot_reply = response.generations[0].text.strip()
        history.append({"role": "bot", "content": bot_reply})

        return jsonify({'history': history})

    return render_template('index.html', history=history, personality="", temperature=0.5)
