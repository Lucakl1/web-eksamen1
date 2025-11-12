from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import x 
import time
import uuid
import os

from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

app = Flask(__name__)

# Set the maximum file size to 10 MB
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024   # 1 MB

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
 

##############################
##############################
##############################
def _____USER_____(): pass 
##############################
##############################
##############################

@app.get("/")
def view_index():
    return render_template("index.html")

##############################
@app.get("/login")
#@x.no_cache
def view_login():
    try:
        user_email = session.get("user_email", "")
        user_password = session.get("user_password", "")

        return render_template("login.html", user_email=user_email, user_password=user_password)
    except Exception as ex:
        ic(ex)
    finally:
        pass

@app.get("/logout")
def view_logout():
    try:
        session.clear()
        return "User logged out"
    except Exception as ex:
        ic(ex)
        return "something went wrong try again"
    finally:
        pass

##############################
##############################
##############################
@app.post("/login")
def handle_login():
    try:
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()

        db, cursor = x.db()
        db.start_transaction()
        q = "SELECT * FROM users WHERE user_email = %s AND user_password = %s"
        cursor.execute(q, (user_email, user_password))
        user = cursor.fetchone()
        if not user: raise Exception("user not fount", 400)

        session["user_email"] = user["user_email"]
        session["user_password"] = user["user_password"]

        db.commit()

        return "logged success"
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()

        if "Twitter exception - Invalid password" in str(ex):
            return "Email or Password is invalid", 400
        
        if "Twitter exception - Invalid email" in str(ex):
            return "Email or Password is invalid", 400
        
        if "user not fount" in str(ex):
            return "no user found"


        return "System under maintenece"
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()






















