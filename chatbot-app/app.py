from flask import Flask, render_template, request
import cohere
import os

app = Flask(__name__)
co = cohere.Client(os.environ.get("COHERE_API_KEY"))  # Use env variable

@app.route('/', methods=['GET', 'POST'])
def chatbot():
    response_text = ""
    if request.method == 'POST':
        personality = request.form['personality']
        temp = float(request.form['temperature'])
        chat_input = request.form['user_input']

        chat_history = personality.strip().split("\n")
        chat_history.append(f"you: {chat_input}")
        prompt = "\n".join(chat_history) + "\nbot:"

        response = co.generate(
            model='command-light',
            prompt=prompt,
            max_tokens=100,
            temperature=temp
        )

        bot_reply = response.generations[0].text.strip()
        response_text = bot_reply

    return render_template('index.html', response=response_text)

if __name__ == '__main__':
    app.run()
