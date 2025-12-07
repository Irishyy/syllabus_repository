import sqlite3 as lit
import os

def get_connection():
  os.makedirs('data', exist_ok=True)
  conn = lit.connect('data/syllabi.db')
  return conn

def init_database():
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS syllabi (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      course_code TEXT NOT NULL,
      course_name TEXT NOT NULL,
      instructor TEXT NOT NULL,
      semester TEXT NOT NULL,
      year INTEGER NOT NULL,
      current_version INTEGER DEFAULT 1,
      added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
  ''')

  # Syllabi versions table (stores all versions)
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS syllabus_versions (
      version_id INTEGER PRIMARY KEY AUTOINCREMENT,
      syllabus_id INTEGER NOT NULL,
      version_number INTEGER NOT NULL,
      pdf_path TEXT NOT NULL,
      created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      change_notes TEXT,
      FOREIGN KEY (syllabus_id) REFERENCES syllabi(id) ON DELETE CASCADE,
      UNIQUE(syllabus_id, version_number)
    )
  ''')

  cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT NOT NULL UNIQUE,
          password TEXT NOT NULL
        )
  ''')

  cursor.execute('''
    INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)          
  ''', ('admin', '81dc9bdb52d04dc20036dbd8313ed055'))

  conn.commit()
  conn.close()
  print("Database initialized with versioning support.")

if __name__ == "__main__":
  init_database()