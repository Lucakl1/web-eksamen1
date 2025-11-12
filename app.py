from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import x 
import time
import uuid
import os
from icecream import ic

app = Flask(__name__)

##############################
##############################
##############################
def _____USER_____(): pass 
##############################
##############################
##############################

##############################
##############################
@app.route("/test", methods=["GET","POST"])
@app.route("/test/<test_name>", methods=["GET","POST"])
def view_tests(test_name = "all"):
    try:
        if test_name == "all":
            all_the_html = ""
            templates_path = os.listdir(os.path.join(app.root_path, 'templates/test'))
            for file in templates_path:
                all_the_html += render_template(f"test/{file}")
            return all_the_html
        return render_template(f"test/{test_name}.html")
    except:
        return "either no pages was found, or an error in the code"
    
@app.post('/upload')
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    file.save(os.path.join("static/uploads", file.filename))
    return redirect("/test")
##############################
##############################

@app.get("/")
def view_index():
    return render_template("index.html")