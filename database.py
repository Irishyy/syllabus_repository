import sqlite3 as lit
import os

def get_connection():
  os.makedirs('data', exist_ok=True) # exist_ok=True is a named argument that the os.makedirs() function checks internally to see if the directory already exists. If it does, it won't raise an error.
  conn = lit.connect('data/syllabi.db')
  return conn

# Syllabi table (Create)

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
      pdf_path TEXT NOT NULL,
      added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
  ''')

  # Users table (Create w/ simple auth)
  cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT NOT NULL UNIQUE,
          password TEXT NOT NULL
        )
  ''') # Primary key makes sure each user has a unique identifier # Unique constraint ensures no duplicate usernames

  # Insert default admin user (username: admin, password: 1234)

  cursor.execute('''
    INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)          
  ''', ('admin', '81dc9bdb52d04dc20036dbd8313ed055')) # MD5 hash for '1234' # Using parameterized query to prevent SQL injection # INSERT OR IGNORE to avoid duplicate entries. Basically, if it violates the UNIQUE constraint, it will ignore the insertion instead of throwing an error.

  conn.commit()
  conn.close()
  print("Database initialized.")

if __name__ == "__main__":
  init_database()

# Every Python file can be run as a script. When you run a file directly, Python sets a special built-in variable called __name__ to "__main__". This allows you to include code that should only execute when the file is run directly, and not when it's imported as a module in another file.
# But if the file is imported as a module in another script, the code inside this block will not run. The vaiable __name__ will be set to the module's name instead. In this case, it would be "database".
