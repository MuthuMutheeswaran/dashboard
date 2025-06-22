import os
import psycopg2
import openpyxl
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file

app = Flask(__name__)
app.secret_key = "your-secret-key"

# PostgreSQL Config
POSTGRES_CONFIG = {
    'host': 'dpg-d1br9kbe5dus73esr1hg-a',
    'user': 'quiz_db_4gch_user',
    'password': 'kXoWWGPKSjq52aM1H8hX0qp2KFQbj5KZ',
    'dbname': 'quiz_db_4gch'
}

def get_db_connection():
    return psycopg2.connect(**POSTGRES_CONFIG)

@app.route("/")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT id, topic, username, created_at FROM quizzes ORDER BY created_at DESC")
    quizzes = cursor.fetchall()

    cursor.execute("SELECT username, name, score, total_questions FROM quiz_results")
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("dashboard.html", users=users, quizzes=quizzes, results=results)

@app.route("/dashboard/add_user", methods=["POST"])
def add_user():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        flash("User already exists!", "warning")
    else:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        flash("User added successfully!", "success")

    cursor.close()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/dashboard/delete_user", methods=["POST"])
def delete_user():
    username = request.form.get("username")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("User deleted successfully!", "info")
    return redirect(url_for("dashboard"))
@app.route("/dashboard/delete_quiz", methods=["POST"])
def delete_quiz():
    quiz_id = request.form.get("quiz_id")
    if not quiz_id:
        flash("Quiz ID is required", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM quizzes WHERE id = %s", (quiz_id,))
            conn.commit()
            flash("Quiz deleted successfully!", "success")
        except Exception as e:
            flash(f"Error deleting quiz: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for("dashboard"))

@app.route("/dashboard/download_results")
def download_results():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, score, total_questions FROM quiz_results")
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create Excel file
    file_path = "quiz_results.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Results"
    sheet.append(["Username", "Name", "Score", "Total Questions"])
    for row in results:
        sheet.append(row)
    workbook.save(file_path)

    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port, host="0.0.0.0")
