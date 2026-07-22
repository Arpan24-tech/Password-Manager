import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
from database import register_user, verify_user, add_vault_entry, get_vault_entries

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key_12345")

# --- Page Routes ---

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard_page"))
    return redirect(url_for("login_page"))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("dashboard.html", username=session.get("username"))

# --- Authentication API Endpoints ---

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json or {}
    username = data.get("username", "").strip()
    master_password = data.get("master_password", "").strip()

    if not username or not master_password:
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    success, message = register_user(username, master_password)
    if success:
        return jsonify({"status": "success", "message": message})
    return jsonify({"status": "error", "message": message}), 400

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    username = data.get("username", "").strip()
    master_password = data.get("master_password", "").strip()

    user = verify_user(username, master_password)
    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        # Store master password and salt temporarily in session for key derivation
        session["master_password"] = master_password
        session["salt"] = user["salt"].hex()  # Store salt as hex string
        return jsonify({"status": "success", "message": "Login successful!"})

    return jsonify({"status": "error", "message": "Invalid username or master password."}), 401

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

# --- Vault Operations API Endpoints ---

@app.route("/api/vault/add", methods=["POST"])
def api_vault_add():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.json or {}
    service = data.get("service", "").strip()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not service or not username or not password:
        return jsonify({"status": "error", "message": "All vault fields are required."}), 400

    user_id = session["user_id"]
    master_password = session["master_password"]
    salt = bytes.fromhex(session["salt"])

    add_vault_entry(user_id, master_password, salt, service, username, password)
    return jsonify({"status": "success", "message": f"Credential for '{service}' saved successfully!"})

@app.route("/api/vault/get", methods=["GET"])
def api_vault_get():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    user_id = session["user_id"]
    master_password = session["master_password"]
    salt = bytes.fromhex(session["salt"])

    entries = get_vault_entries(user_id, master_password, salt)
    return jsonify({"status": "success", "entries": entries})

if __name__ == "__main__":
    app.run(debug=True)