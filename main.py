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

MODELS = ["gemini-2.5-flash", "gemini-1.5-flash"]

def call_gemini(prompt):
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            answer = result["candidates"][0]["content"]["parts"][0]["text"]
            return answer, model
        except Exception:
            continue
    return "Sorry, AI service is temporarily unavailable. Please try again.", "none"

@app.route("/", methods=["GET"])
def home():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>AI Resume Agent 🚀</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background: #f0f4ff; min-height: 100vh; }
        .header { background: linear-gradient(135deg, #1a73e8, #0d47a1); color: white; padding: 20px; text-align: center; }
        .header h1 { font-size: 24px; }
        .header p { font-size: 13px; opacity: 0.85; margin-top: 5px; }
        .tabs { display: flex; background: white; border-bottom: 2px solid #e0e0e0; }
        .tab { flex: 1; padding: 14px; text-align: center; cursor: pointer; font-weight: bold; color: #666; border-bottom: 3px solid transparent; }
        .tab.active { color: #1a73e8; border-bottom: 3px solid #1a73e8; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .section { display: none; }
        .section.active { display: block; }
        .chat-box { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .messages { height: 300px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #fafafa; }
        .msg { margin: 10px 0; padding: 10px 14px; border-radius: 18px; max-width: 80%; line-height: 1.5; }
        .msg.user { background: #1a73e8; color: white; margin-left: auto; border-radius: 18px 18px 4px 18px; }
        .msg.bot { background: white; border: 1px solid #e0e0e0; color: #333; border-radius: 18px 18px 18px 4px; }
        .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
        .chip { background: #e8f0fe; color: #1a73e8; border: 1px solid #1a73e8; border-radius: 20px; padding: 6px 14px; cursor: pointer; font-size: 13px; }
        .chip:hover { background: #1a73e8; color: white; }
        .input-row { display: flex; gap: 10px; }
        .input-row input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
        .input-row button { background: #1a73e8; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .input-row button:hover { background: #0d47a1; }
        .match-box { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .match-box h3 { color: #1a73e8; margin-bottom: 12px; }
        textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; resize: vertical; font-family: Arial; }
        .match-btn { background: linear-gradient(135deg, #1a73e8, #0d47a1); color: white; border: none; padding: 14px 30px; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: bold; margin-top: 12px; width: 100%; }
        .match-btn:hover { opacity: 0.9; }
        .result-box { margin-top: 20px; background: #f0f7ff; border-left: 4px solid #1a73e8; border-radius: 8px; padding: 16px; white-space: pre-wrap; line-height: 1.7; display: none; }
        .score-big { font-size: 48px; font-weight: bold; color: #1a73e8; text-align: center; margin: 10px 0; }
        .loading { color: #1a73e8; text-align: center; padding: 20px; display: none; }
        .tag { background: #e8f0fe; color: #1a73e8; border-radius: 12px; padding: 3px 10px; font-size: 12px; margin: 3px; display: inline-block; }
    </style>
</head>
<body>
<div class="header">
    <h1>🤖 AI Resume Agent</h1>
    <p>Powered by Google Gemini • Built by Bhawana Verma</p>
</div>
<div class="tabs">
    <div class="tab active" onclick="showTab('chat')">💬 Resume Chat</div>
    <div class="tab" onclick="showTab('match')">🎯 Job Matcher</div>
</div>
<div class="container">

    <!-- CHAT TAB -->
    <div class="section active" id="chat">
        <br>
        <div class="chat-box">
            <div class="chips">
                <span class="chip" onclick="ask('What are the key skills?')">🛠️ Skills</span>
                <span class="chip" onclick="ask('Describe the work experience.')">💼 Experience</span>
                <span class="chip" onclick="ask('What certifications does she have?')">🏆 Certifications</span>
                <span class="chip" onclick="ask('What is the educational background?')">🎓 Education</span>
                <span class="chip" onclick="ask('Is this candidate suitable for a cloud engineer role?')">☁️ Cloud Fit?</span>
            </div>
            <div class="messages" id="messages">
                <div class="msg bot">👋 Hi! I am Bhawana\'s AI Resume Agent. Ask me anything about her resume!</div>
            </div>
            <div class="input-row">
                <input type="text" id="userInput" placeholder="Ask anything about the resume..." onkeypress="if(event.key===\'Enter\') ask()"/>
                <button onclick="ask()">Send ➤</button>
            </div>
        </div>
    </div>

    <!-- JOB MATCHER TAB -->
    <div class="section" id="match">
        <br>
        <div class="match-box">
            <h3>🎯 Job Description Matcher</h3>
            <p style="color:#666; font-size:13px; margin-bottom:12px;">Paste any job description below — AI will analyze how well this resume matches and suggest improvements!</p>
            <textarea id="jobDesc" rows="8" placeholder="Paste the job description here...&#10;&#10;Example:&#10;We are looking for a Cloud Engineer with experience in GCP, Python, and AI/ML..."></textarea>
            <button class="match-btn" onclick="matchJob()">🔍 Analyze Match</button>
            <div class="loading" id="matchLoading">⏳ Analyzing your resume against the job description...</div>
            <div class="result-box" id="matchResult"></div>
        </div>
    </div>

</div>
<script>
function showTab(tab) {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
    document.getElementById(tab).classList.add("active");
    event.target.classList.add("active");
}
function ask(q) {
    const input = document.getElementById("userInput");
    const query = q || input.value.trim();
    if (!query) return;
    addMsg(query, "user");
    input.value = "";
    addMsg("⏳ Thinking...", "bot", "thinking");
    fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({prompt: query})
    })
    .then(r => r.json())
    .then(data => {
        document.getElementById("thinking")?.remove();
        addMsg(data.answer || data.error, "bot");
    })
    .catch(() => {
        document.getElementById("thinking")?.remove();
        addMsg("Sorry, something went wrong. Please try again.", "bot");
    });
}
function addMsg(text, type, id) {
    const box = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = "msg " + type;
    if (id) div.id = id;
    div.innerText = text;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}
function matchJob() {
    const jd = document.getElementById("jobDesc").value.trim();
    if (!jd) { alert("Please paste a job description first!"); return; }
    document.getElementById("matchLoading").style.display = "block";
    document.getElementById("matchResult").style.display = "none";
    fetch("/match", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({job_description: jd})
    })
    .then(r => r.json())
    .then(data => {
        document.getElementById("matchLoading").style.display = "none";
        const box = document.getElementById("matchResult");
        box.style.display = "block";
        box.innerText = data.result || data.error;
    })
    .catch(() => {
        document.getElementById("matchLoading").style.display = "none";
        document.getElementById("matchResult").style.display = "block";
        document.getElementById("matchResult").innerText = "Error occurred. Please try again.";
    });
}
</script>
</body>
</html>'''

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_query = data.get("prompt", "Summarize this resume.") if data else "Summarize this resume."
    full_prompt = f"""You are an AI Resume Assistant. Answer questions about this resume only.
Resume: {resume_context}
Question: {user_query}
Answer clearly and professionally."""
    answer, model_used = call_gemini(full_prompt)
    return jsonify({"answer": answer, "model": model_used})

@app.route("/match", methods=["POST"])
def match_job():
    data = request.json
    job_desc = data.get("job_description", "") if data else ""
    if not job_desc:
        return jsonify({"error": "Please provide a job description."}), 400
    match_prompt = f"""You are an expert HR analyst and career coach. Analyze this resume against the job description.

RESUME:
{resume_context}

JOB DESCRIPTION:
{job_desc}

Provide a detailed analysis with:
1. MATCH SCORE: X/100
2. STRONG MATCHES: Skills and experience that align well
3. GAPS: Missing skills or experience
4. RECOMMENDATIONS: How to improve the resume for this role
5. VERDICT: Should apply? Yes/No/Maybe with reason

Be specific, honest, and helpful."""
    result, model_used = call_gemini(match_prompt)
    return jsonify({"result": result, "model": model_used})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
