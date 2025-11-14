from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import requests
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import csv, io, json, time, uuid, os

# other python files
import x

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
        x = x,
    )

@app.get("/logout")
def logout():
    try:
        session.clear()
        return redirect(url_for("login"))
    except Exception as ex:
        ic(ex)
        return "error"

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
    
    # til senere sæt en path i x filen UPLOAD_ITEM_FOLDER = './images'
    file.save(os.path.join("static/uploads", file.filename))
    return redirect("/test")
##############################
##############################

@app.get("/home")
@app.get("/")
def view_index():
    try:
        if not session.get("user", ""): return redirect(url_for("login"))
        return render_template("index.html")
    except Exception as ex:
        ic(ex)
        return "error"

@app.route("/login", methods=["GET", "POST"])
@app.route("/login/<lan>", methods=["GET", "POST"])
def login(lan = "en"):
    try:
        if lan not in x.allowed_languages: lan = "english"
        x.default_language = lan

        if request.method == "GET":
            try:
                if session.get("user", ""): return redirect("/")
                return render_template("login.html")
            except Exception as ex:
                ic(ex)
                return "error"

        if request.method == "POST":

            user_email_or_username = request.form.get("user_email_username", "").strip()

            if "@" in user_email_or_username:
                user_email = x.validate_user_email(user_email_or_username)
                user_password = x.validate_user_password()

                db, cursor = x.db()
                q = "SELECT * FROM users WHERE user_email = %s"
                cursor.execute(q, (user_email,))
                user = cursor.fetchone()

                if not user: raise Exception(f"x exception - {x.lans('email_or_password_is_wrong')}", 400)

                if not check_password_hash(user["user_password"], user_password):
                    raise Exception(f"x exception - {x.lans('email_or_password_is_wrong')}", 400)

            else:
                user_username = x.validate_user_username(user_email_or_username)
                user_password = x.validate_user_password()

                db, cursor = x.db()
                q = "SELECT * FROM users WHERE user_username = %s"
                cursor.execute(q, (user_username,))
                user = cursor.fetchone()

                if not user: raise Exception(f"x exception - {x.lans('username_or_password_is_wrong')}", 400)

                if not check_password_hash(user["user_password"], user_password):
                    raise Exception(f"x exception - {x.lans('username_or_password_is_wrong')}")
                
                
            if user["user_varified_at"] == "":
                raise Exception(f"x exception - {x.lans('user_not_verified')}", 400)  

            user.pop("user_password")
            user["user_language"] = lan

            session["user"] = user

            return f"""<browser mix-redirect='/home'></browser>"""

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = "error" #should i say system under maintenese? #### TO ASK ####
        if("x exception - " in error_code):
            error_msg = error_code.replace("('x exception - ", "").split("', ")[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.route("/signup", methods=["GET", "POST"])
@app.route("/signup/<lan>", methods=["GET", "POST"])
def signup(lan = "en"):
    try:
        if lan not in x.allowed_languages: lan = "english"
        x.default_language = lan

        if request.method == "GET":
            try:
                if session.get("user", ""): return redirect("/")
                return render_template("signup.html")
            except Exception as ex:
                ic(ex)
                return "error"

        if request.method == "POST":
            
            user_email = x.validate_user_email()
            user_language = x.validate_user_language()
            user_password = x.validate_user_password()
            user_confirm_password = x.validate_user_password_confirm()
            user_phone = x.validate_user_phone()
            user_usernmae = x.validate_user_username()
            user_first_name = x.validate_user_first_name()
            user_last_name = x.validate_user_last_name()
            current_time = time.time()                          # make epoch time if not allready

            db, cursor = x.db()
            q = "INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            # user_pk | user_first_name | user_last_name | user_last_name | user_username | user_email | user_password | user_language | role_fk | user_banner | user_avatar | user_bio | user_total_followers | user_total_following | user_total_likes | user_total_posts | user_created_at | user_varified_at | user_updated_at | user_deletet_at
            cursor.execute(q, ('default', user_first_name, user_last_name, user_usernmae, user_email, user_password, x.default_language, 'default', 'default', 'default', 'default', 'default', 'default', 'default', 'default', current_time, varify, 'default', 'default'))

            pass

    except Exception as ex:
        ic(ex)
        return "error"
    finally:
        pass

##############################
########## utilities #########
##############################
@app.get("/get-data-from-sheet")
def get_data_from_sheet():
    try:
        # Check if the admin is running this end-point, else show error
 
        # key: 1UYgE2jJ__HYl0N7lA5JR3sMH75hwhzhPPsSRRA-WNdg
        url= f"https://docs.google.com/spreadsheets/d/{x.google_spread_sheet_key}/export?format=csv&id={x.google_spread_sheet_key}"
        res=requests.get(url=url)
        # return(res.text) # retuns a page if there is an error
        csv_text = res.content.decode('utf-8')
        csv_file = io.StringIO(csv_text) # Use StringIO to treat the string as a file
       
        data = {}
        reader = csv.DictReader(csv_file)
        #ic(reader)
        # Convert each row into the desired structure
        for row in reader:
            item = {
                    'english': row['english'],
                    'danish': row['danish'],
                    'spanish': row['spanish']
               
            }
            data[row['key']] = (item)
 
        # Convert the data to JSON
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        # ic(data)
 
        # Save data to the file
        with open("dictionary.json", 'w', encoding='utf-8') as f:
            f.write(json_data)
 
        return f"data has been saved <br> <br> {json_data}"
    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
        pass