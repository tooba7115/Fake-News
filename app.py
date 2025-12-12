from flask import Flask, render_template, session, request, redirect
import sqlite3, random, os

app = Flask(__name__)
app.secret_key = "change-me"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "FakeNews.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    try:
        if "correct" not in session:
            session["correct"] = 0
            session["total"] = 0

        conn = get_db()
        headline = conn.execute("SELECT * FROM FakeNews ORDER BY RANDOM() LIMIT 1").fetchone()
        conn.close()

        if headline is None:
            return "Database is empty or table name is wrong."

        return render_template("index.html", h=headline)

    except Exception as e:
        return f"Error loading index page: {e}"

@app.route("/answer", methods=["POST"])
def answer():
    headline_id = request.form['id']
    user_guess = request.form['guess']

    conn = get_db()
    h = conn.execute("SELECT * FROM FakeNews WHERE id = ?", (headline_id,)).fetchone()
    conn.close()

    correct_answer = h["realOrFake"]

    session['total'] += 1
    is_correct = (user_guess == correct_answer)

    if is_correct:
        session['correct'] += 1

    return render_template('results.html', h=h, is_correct=is_correct, user_guess=user_guess)

@app.route("/reset")
def reset():
    session.clear()
    return redirect("/")

@app.route('/progress')
def progress():
    correct = session.get('correct', 0)
    total = session.get("total", 0)
    wrong = total - correct

    return render_template('progress.html', correct=correct, wrong=wrong, total=total)

if __name__ == "__main__":
    app.run(debug=True)