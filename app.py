from flask import Flask, redirect, render_template, request, g
import sqlite3
import os

app = Flask(__name__)



# --- FUNGSI INISIALISASI DATABASE ---

def get_db_connection():
    # Menggunakan mode ":memory:"
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    conn.row_factory = sqlite3.Row # Mengizinkan akses kolom by name
    return conn

def init_db(conn):
    cursor = conn.cursor()
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

# --- INISIALISASI GLOBAL (Hanya Sekali Saat Startup) ---
try:
    GLOBAL_CONN = get_db_connection()
    init_db(GLOBAL_CONN)
except Exception as e:
    # Penting: Jika inisialisasi gagal, Gunicorn akan tetap mencoba memulai
    print(f"FATAL ERROR during in-memory DB initialization: {e}")


# --- ROUTES APLIKASI ---

@app.route('/addTask', methods=['GET'])
def add_task():
    conn = GLOBAL_CONN
    cursor = conn.cursor()
    # Mengambil task dari query string
    task = request.args.get('task')
    
    if task:
        # Parameterisasi: Mencegah SQL Injection
        cursor.execute("INSERT INTO tasks(task) VALUES(?)", (task,))
        conn.commit()
    return redirect('/')

@app.route('/move-to-done/<int:id>/<string:task_name>')
def move_to_done(id, task_name):
    conn = GLOBAL_CONN
    cursor = conn.cursor()
    
    # 1. Pindahkan ke tabel 'done'
    # Parameterisasi digunakan untuk memastikan keamanan data
    cursor.execute("INSERT INTO done(task, task_id) VALUES(?,?)", (task_name, id))
    
    # 2. Hapus dari tabel 'tasks'
    cursor.execute("DELETE FROM tasks WHERE tid = ?", (id,))
    
    conn.commit()
    return redirect('/')

@app.route('/deleteTask/<int:id>')
def deleteTask(id):
    conn = GLOBAL_CONN
    cursor = conn.cursor()
    # Menghapus task dari daftar todo
    cursor.execute("DELETE FROM tasks WHERE tid=?", (id,))
    conn.commit()
    return redirect('/')


@app.route('/delete-completed/<int:id>')
def deleteCompletedTask(id):
    conn = GLOBAL_CONN
    cursor = conn.cursor()
    # Menghapus task dari daftar selesai
    cursor.execute("DELETE FROM done WHERE did=?", (id,))
    conn.commit()
    return redirect('/')


@app.route('/')
def home():
    conn = GLOBAL_CONN
    cursor = conn.cursor()
    
    # Ambil semua tasks (ID dan Nama Task)
    cursor.execute("SELECT tid, task FROM tasks ORDER BY tid DESC")
    # Menggunakan list comprehension untuk format yang lebih bersih (jika tidak menggunakan row_factory)
    tasks = [(row[0], row[1]) for row in cursor.fetchall()]
    
    # Ambil semua done tasks
    cursor.execute("SELECT did, task FROM done ORDER BY did DESC")
    done = [(row[0], row[1]) for row in cursor.fetchall()]
    
    return render_template('index.html', tasks=tasks, done=done)