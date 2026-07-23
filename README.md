# 🔐 Secure Web-Based Password Manager

A full-stack web application that allows users to securely manage, store, and organize their credentials in a centralized, encrypted vault environment. Built with **Python** and **Flask**, integrated with **PostgreSQL**, and deployed live on **Render**.

## ✨ Features

* **User Authentication:** Secure registration, login, and session management using hashed passwords.
* **Personal Vault Dashboard:** Clean UI to view, search, add, and delete stored account credentials.
* **Relational Database Storage:** Seamless transition from local SQLite to production-grade PostgreSQL.
* **Environment-Based Config:** Secure management of database URIs and secret keys using environment variables.
* **Continuous Deployment:** Integrated CI/CD via GitHub and Render cloud platform.

---

## 🛠️ Tech Stack

### **Backend**
* **Language:** Python 3
* **Framework:** Flask
* **ORM:** Flask-SQLAlchemy
* **Security & Auth:** Werkzeug (Password Hashing)

### **Frontend**
* **Templating:** Jinja2
* **Languages:** HTML5, CSS3, JavaScript

### **Database & Deployment**
* **Database:** PostgreSQL (Production on Render), SQLite (Local Development)
* **Hosting Platform:** Render Web Service & Managed PostgreSQL
* **Tools:** Git, GitHub, VS Code, Database Client

---

## 📂 Project Structure

```text
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
├── templates/
│   ├── dashboard.html
│   ├── login.html
│   └── register.html
├── .env
├── .gitignore
├── app.py
├── database.py
├── requirements.txt
└── README.md

🚀 Local Getting Started Guide
Follow these instructions to run the project locally on your machine.

```Prerequisites
Python 3.10+ installed
Git installed
```
1. Clone the Repository
```Bash
git clone https://github.com/Arpan24-tech/Password-Manager.git
cd your-repo-name
```
2. Create and Activate a Virtual Environment
Windows:
```Bash
python -m venv venv
.\venv\Scripts\activate
```
macOS/Linux:
```Bash
python3 -m venv venv
source venv/bin/activate
```
3. Install Dependencies
```Bash
pip install -r requirements.txt
```
4. Configure Environment Variables
Create a .env file in the root directory and add:
```Code snippet
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///app.db
```
5. Run the Application
```Bash
python app.py
```
Open your browser and navigate to http://127.0.0.1:5000.
