from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from openai import OpenAI

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required
)

app = Flask(__name__)

load_dotenv()

# OpenAI Config
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# JWT Config
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

jwt = JWTManager(app)


@app.route("/")
def hello_world():
    return render_template("index.html")


# LOGIN API
@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    # UAT Hardcoded User
    if username == "admin" and password == "admin123":

        token = create_access_token(
            identity=username
        )

        return jsonify({
            "token": token
        }), 200

    return jsonify({
        "message": "Invalid Credentials"
    }), 401


# PROTECTED ASK API
@app.route("/ask", methods=["POST"])
@jwt_required()
def ask():

    question = request.form.get("question")

    try:

        response = client.responses.create(
            model="gpt-5",
            input=[
                {
                    "role": "system",
                    "content": "Act like a helpful personal assistant"
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        answer = response.output_text.strip()

        return jsonify({
            "response": answer
        }), 200

    except Exception as e:

        return jsonify({
            "response": str(e)
        }), 500


# PROTECTED SUMMARIZE API
@app.route("/summarize", methods=["POST"])
@jwt_required()
def summarize():

    email_text = request.form.get("email")

    prompt = f"Summarize the following email in 2-3 sentences: {email_text}"

    try:

        response = client.responses.create(
            model="gpt-5",
            input=[
                {
                    "role": "system",
                    "content": "Act like an expert email assistant"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        summary = response.output_text.strip()

        return jsonify({
            "response": summary
        }), 200

    except Exception as e:

        return jsonify({
            "response": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)