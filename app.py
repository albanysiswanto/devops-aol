from flask import Flask, redirect, render_template, request
import sqlite3
import os

app = Flask(__name__)

# --- FUNGSI INI TERPISAH DARI APLIKASI WEB ---
# FUNGSI UNTUK INISIALISASI DATABASE IN-MEMORY
# PERINGATAN: Data akan hilang saat container didaur ulang
def get_db_connection():
    # Menggunakan mode ":memory:" agar database berada di RAM dan tidak ada masalah I/O file
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    return conn

# Fungsi untuk membuat tabel saat aplikasi dimulai
def init_db(conn):
    cursor = conn.cursor()
    # Hati-hati dengan sintaks, pastikan tabel memiliki primary key untuk id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            tid INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS done (
            did INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            task_id INTEGER
        )
    """)
    conn.commit()

# --- INISIALISASI DATABASE IN-MEMORY SECARA GLOBAL ---
# Kita tetap melakukan ini di luar, tapi karena :memory:, ini aman untuk boot
try:
    GLOBAL_CONN = get_db_connection()
    init_db(GLOBAL_CONN)
except Exception as e:
    # Log error jika inisialisasi gagal, tapi tidak akan menghentikan Gunicorn
    print(f"ERROR initializing in-memory DB: {e}")

# --- ROUTES APLIKASI ---

@app.route('/addTask', methods=['GET'])
def add_task():
    # Menggunakan koneksi global (karena :memory: dan check_same_thread=False)
    conn = GLOBAL_CONN
    cursor = conn.cursor()
    task = request.args.get('task')
    if task:
        cursor.execute("INSERT INTO tasks(task) VALUES(?)", (task,))
        conn.commit()
    return redirect('/')

# Endpoint ini tidak diperlukan karena 'home' sudah mengambil semua tugas
# @app.route('/getTasks', methods=['GET'])
# def get_tasks():
#    return redirect('/')

@app.route('/move-to-done/<int:id>/<string:task_name>')
def move_to_done(id, task_name):
    conn = GLOBAL_CONN
    cursor = conn.cursor()
    # Pastikan task_name tidak kosong sebelum insert
    if task_name:
        cursor.execute("INSERT INTO done(task, task_id) VALUES(?,?)", (task_name, id))
        cursor.execute("DELETE FROM tasks WHERE tid = ?", (id,))
        conn.commit()
    return redirect('/')

@app.route('/deleteTask/<int:id>')
def deleteTask(id):
    conn = GLOBAL_CONN
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE tid=?", (id,))
    conn.commit()
    return redirect('/')


@app.route('/delete-completed/<int:id>')
def deleteCompletedTask(id):
    conn = GLOBAL_CONN
    cursor = conn.cursor()
    cursor.execute("DELETE FROM done WHERE did=?", (id,))
    conn.commit()
    return redirect('/')


@app.route('/')
def home():
    # Menggunakan koneksi global yang sudah diinisialisasi
    conn = GLOBAL_CONN
    cursor = conn.cursor()
    
    # Ambil semua tasks
    cursor.execute("SELECT tid, task FROM tasks ORDER BY tid DESC")
    tasks = cursor.fetchall() 
    
    # Ambil semua done tasks
    cursor.execute("SELECT did, task FROM done ORDER BY did DESC")
    done = cursor.fetchall()
    
    # Note: Flask Jinja2 akan mengakses data di index.html
    return render_template('index.html', tasks=tasks, done=done)


# Baris yang menjalankan aplikasi secara lokal dihapus, karena Gunicorn yang akan menjalankannya
# if __name__ == "__main__":
#     app.run(debug=True)
#     run_terraform()