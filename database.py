import os
import base64
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

load_dotenv()

# --- Database Connection ---
DATABASE_URL = os.getenv("DATABASE_URL") 

def get_db_connection():
    if DATABASE_URL:
        # Runs on Render (Cloud DB)
        url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    else:
        # Runs on your local machine
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
# --- User Authentication ---
def register_user(username, master_password):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if username exists
    cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
    if cur.fetchone():
        conn.close()
        return False, "Username already exists."

    # Hash master password for login validation & generate salt for encryption key derivation
    password_hash = generate_password_hash(master_password)
    salt = os.urandom(16)

    cur.execute(
        "INSERT INTO users (username, password_hash, salt) VALUES (%s, %s, %s);",
        (username, password_hash, psycopg2.Binary(salt))
    )
    conn.commit()
    conn.close()
    return True, "User registered successfully!"

def verify_user(username, master_password):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, password_hash, salt FROM users WHERE username = %s;", (username,))
    user = cur.fetchone()
    conn.close()

    if user and check_password_hash(user[1], master_password):
        user_id, _, salt = user
        return {"id": user_id, "username": username, "salt": bytes(salt)}
    
    return None

# --- Vault Operations ---
def add_vault_entry(user_id, master_password, salt, service, username, password):
    key = derive_key(master_password, salt)
    fernet = Fernet(key)
    encrypted_pass = fernet.encrypt(password.encode())

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_vaults (user_id, service, username, encrypted_password) VALUES (%s, %s, %s, %s);",
        (user_id, service, username, psycopg2.Binary(encrypted_pass))
    )
    conn.commit()
    conn.close()

def get_vault_entries(user_id, master_password, salt):
    key = derive_key(master_password, salt)
    fernet = Fernet(key)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, service, username, encrypted_password FROM user_vaults WHERE user_id = %s;",
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()

    decrypted_entries = []
    for row in rows:
        entry_id, service, user, enc_pwd = row
        try:
            decrypted_pwd = fernet.decrypt(bytes(enc_pwd)).decode()
            decrypted_entries.append({
                "id": entry_id,
                "service": service,
                "username": user,
                "password": decrypted_pwd
            })
        except Exception:
            continue  # Handles decryption errors if key fails

    return decrypted_entries
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt BYTEA NOT NULL
        );
        CREATE TABLE IF NOT EXISTS user_vaults (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id) ON DELETE CASCADE,
            service VARCHAR(100) NOT NULL,
            username VARCHAR(100) NOT NULL,
            encrypted_password BYTEA NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()