import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

try:
    with open("resume.txt", "r") as f:
        resume_context = f.read()
except FileNotFoundError:
    resume_context = "Resume file not found."

@app.route("/", methods=["POST", "GET"])
def ask_agent():
    user_query = "Summarize this resume."
    if request.method == "POST":
        data = request.json
        if data:
            user_query = data.get("prompt", user_query)

    full_prompt = f"Resume Context: {resume_context}\n\nQuestion: {user_query}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload)
        result = response.json()
        answer = result["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e), "raw": str(result)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
