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

def _____USER_____(): pass 
##############################
##############################
##############################

########### Set up ###########
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.context_processor
def global_variables():
    return dict (
        site_name = request.path.replace("/", " "),
        user_role = session.get("user", ""),
        x = x
    )

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
    try:
        if not session.get("user", ""): return redirect(url_for("login"))
        return render_template("index.html")
    except Exception as ex:
        ic(ex)
        return "error"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        try:
            if session.get("user", ""): return redirect("/")
            return render_template("login.html")
        except Exception as ex:
            ic(ex)
            return "error"

    if request.method == "POST":
        pass

@app.get("/get-data-from-sheet")
def get_data_from_sheet():
    try:
        # Check if the admin is running this end-point, else show error
 
        # flaskwebmail
        url= f"https://docs.google.com/spreadsheets/d/{x.google_spread_sheet_key}/export?format=csv&id={x.google_spread_sheet_key}"
        res=requests.get(url=url)
        # ic(res.text) # contains the csv text structure
        csv_text = res.content.decode('utf-8')
        csv_file = io.StringIO(csv_text) # Use StringIO to treat the string as a file
       
        # Initialize an empty list to store the data
        data = {}
 
        # Read the CSV data
        reader = csv.DictReader(csv_file)
        ic(reader)
        # Convert each row into the desired structure
        for row in reader:
            item = {
                    'english': row['en'],
                    'danish': row['da'],
                    'spanish': row['sp']
            }
            # Append the dictionary to the list
            data[row['key']] = (item)
 
        # Convert the data to JSON
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        # ic(data)
 
        # Save data to the file
        with open("dictionary.json", 'w', encoding='utf-8') as f:
            f.write(json_data)
 
        return "Dictonary updated sucessfully"
    except Exception as ex:
        ic(ex)
        return str(ex)