import sqlite3
import json
from datetime import datetime

DB_NAME = "lectures.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lectures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            transcript TEXT,
            summary TEXT,
            notes TEXT,
            quiz TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_lecture(filename, transcript, materials):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO lectures (filename, transcript, summary, notes, quiz)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        filename, 
        transcript, 
        materials['summary'], 
        json.dumps(materials['notes']), 
        json.dumps(materials['quiz'])
    ))
    lecture_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return lecture_id

def get_all_lectures():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename, created_at FROM lectures ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "filename": r[1], "date": r[2]} for r in rows]

def get_lecture_by_id(lecture_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lectures WHERE id = ?', (lecture_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "filename": row[1],
            "transcript": row[2],
            "materials": {
                "summary": row[3],
                "notes": json.loads(row[4]),
                "quiz": json.loads(row[5])
            },
            "date": row[6]
        }
    return None

def delete_lecture(lecture_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM lectures WHERE id = ?', (lecture_id,))
    conn.commit()
    conn.close()
