import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

import config
def init_db():
    try:
        conn = sqlite3.connect("chat.db", check_same_thread=False)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            title TEXT,
            created_at TEXT
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
        """)
        conn.commit()
        return conn, c
    except sqlite3.Error as e:
        raise RuntimeError("Could not create tables") from e



conn, c = init_db()
app = Flask(__name__)
llm = ChatOllama(model=config.model, base_url=config.host)
agent = create_agent(
    model=llm
)

def save_message(session_id, role, content):
    c = conn.cursor()
    c.execute("INSERT INTO messages(session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (session_id, role, content, datetime.now().isoformat()))
    conn.commit()

def get_session(session_id):
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,))
    exists = c.fetchone()
    return exists

def format_messages(session_id,user_input):
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id=? ORDER BY id DESC LIMIT 5", (session_id,))
    previous = [{"role": r[0], "content": r[1]} for r in reversed(c.fetchall())]
    messages = previous + [{"role": "user", "content": user_input}]
    return messages

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id")
    user_input = data.get("message", "")

    if not session_id or not user_input:
        return jsonify({"error": "session_id and message required"}), 400

    session = get_session(session_id)
    if not session:
        title_prompt = [
            {
                "role": "system",
                "content": "Generate a concise 3–5 word title based on user input. No punctuation. No quotes. Strictly "
                           "answer with only the title."
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
        try:
            title_result = agent.invoke({"messages": title_prompt})
        except Exception:
            return jsonify({"error": "LLM not responding"}), 500

        title = title_result["messages"][-1].content.strip()
        c = conn.cursor()
        c.execute(
            "INSERT INTO sessions(session_id, title, created_at) VALUES (?, ?, ?)",
            (session_id, title, datetime.now().isoformat())
        )
        conn.commit()

    try:
        result = agent.invoke(
            {"messages": format_messages(session_id,user_input)}
        )


        bot_reply = result["messages"][-1].content
    except Exception:
        return jsonify({"error": "LLM not responding"}), 500

    save_message(session_id, "user", user_input)
    save_message(session_id, "assistant", bot_reply)

    return jsonify({"reply": bot_reply})


@app.route("/sessions", methods=["GET"])
def sessions_list():
    c = conn.cursor()
    c.execute("SELECT session_id, title, created_at FROM sessions")
    rows = c.fetchall()
    print(rows)
    sessions = [{"session_id": r[0], "title": r[1], "created_at": r[2]} for r in rows]
    return jsonify(sessions)
@app.route("/history/<session_id>", methods=["GET"])
def history(session_id):
    c = conn.cursor()
    c.execute("SELECT role, content, timestamp FROM messages WHERE session_id=? ORDER BY id", (session_id,))
    rows = c.fetchall()
    return jsonify([{"role": r[0], "content": r[1], "timestamp": r[2]} for r in rows])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
