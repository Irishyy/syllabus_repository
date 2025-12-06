import hashlib # hashlib library provides a way to securely hash passwords
from database import get_connection # Importing the get_connection function from database.py to interact with the database

# This is the MD5 hash of the password "1234"
STORED_HASH = "81dc9bdb52d04dc20036dbd8313ed055"

def hash_password(password):
  """Hashes a password using MD5 algorithm."""
  return hashlib.md5(password.encode()).hexdigest()
# The encode() method converts the password string into bytes, which is required by the md5() function. The hexdigest() method returns the hash in a hexadecimal format. If we don't encode the password, the md5() function would raise a TypeError because it expects a bytes-like object. If we don't use hexdigest(), we would get a hash object instead of a string representation of the hash. This string representation is what we typically store in databases for password verification.

def verify_login(username: str, password: str) -> bool:
  """Verifies if the provided username and password match a user in the database."""
  conn = get_connection()
  cursor = conn.cursor()

  hashed_pw = hash_password(password)

  cursor.execute('''
    SELECT * FROM users WHERE username = ? AND password = ?
  ''', (username, hashed_pw))

  user = cursor.fetchone() # Not hardcoding the admin credentials anymore. Instead, we query the users table in the database to check if a user with the provided username and hashed password exists.
  conn.close()

  return user is not None
