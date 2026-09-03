from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import sqlite3

app = Flask(__name__)
app.secret_key = "change-this-secret-before-deploy"

DB_PATH = "textbooks.db"

DEFAULT_TEXTBOOKS = [
    (
        "windows-basics",
        "Windows Security Basics",
        "A practical walkthrough of common Windows security settings and safe habits.",
        "windows security login updates patches malware defense",
        "windows_security_basics.pdf",
        "windows_security_basics.pdf.exe",
    ),
    (
        "phishing-101",
        "Phishing 101",
        "Learn how phishing scams use misleading links, fake urgency, and social engineering.",
        "phishing email scam links trust social engineering",
        "phishing_101.pdf",
        "phishing_101.pdf.scr",
    ),
    (
        "ransomware-defense",
        "Ransomware Defense",
        "Understand how ransomware spreads, what files it targets, and how to stop it.",
        "ransomware encryption backups malware detection recovery",
        "ransomware_defense.pdf",
        "ransomware_defense.pdf.zip",
    ),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS textbooks (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            keywords TEXT,
            expected_filename TEXT,
            actual_filename TEXT
        )
        """
    )

    existing = conn.execute("SELECT COUNT(*) FROM textbooks").fetchone()[0]
    if existing == 0:
        conn.executemany(
            """
            INSERT INTO textbooks (id, title, description, keywords, expected_filename, actual_filename)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            DEFAULT_TEXTBOOKS,
        )

    conn.commit()
    conn.close()


def get_textbooks():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM textbooks ORDER BY title").fetchall()
    conn.close()
    return {row["id"]: dict(row) for row in rows}


init_db()
TEXTBOOKS = get_textbooks()


def get_search_results(query):
    query = (query or "").strip().lower()
    if not query:
        return []

    matches = []
    for textbook_id, book in get_textbooks().items():
        haystack = " ".join([
            book["title"],
            book["description"],
            book["keywords"],
        ]).lower()
        if query in haystack:
            matches.append({
                "title": book["title"],
                "description": book["description"],
                "url": url_for("textbook_site", textbook_id=textbook_id),
            })
    return matches


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if not query:
            return render_template("search.html", error="Please enter a search term.")
        return redirect(url_for("results", q=query))
    return render_template("search.html")


@app.route("/results")
def results():
    query = request.args.get("q", "")
    results = get_search_results(query)
    return render_template("results.html", query=query, results=results)


@app.route("/textbook/<textbook_id>")
def textbook_site(textbook_id):
    book = TEXTBOOKS.get(textbook_id)
    if book is None:
        return redirect(url_for("home"))
    return render_template("textbook.html", book=book, textbook_id=textbook_id)


@app.route("/download/<textbook_id>")
def download_textbook(textbook_id):
    book = TEXTBOOKS.get(textbook_id)
    if book is None:
        return redirect(url_for("home"))
    return render_template(
        "download_simulation.html",
        expected_filename=book["expected_filename"],
        actual_filename=book["actual_filename"],
        textbook_id=textbook_id,
    )


@app.route("/why-dangerous")
def why_dangerous():
    return render_template("why_dangerous.html")


if __name__ == "__main__":
    app.run(debug=True)