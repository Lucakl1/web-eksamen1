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
        x = x,
        user = session.get("user", "")
    )

@app.get("/logout")
def logout():
    try:
        session.clear()
        return redirect(url_for("login"))
    except Exception as ex:
        ic(ex)
        error_template = render_template(("global/error_message.html"), message=x.lans("error_please_try_again"))
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""

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

@app.get("/")
def view_index():
    try:
        x.site_name = x.lans("home")
        user = session.get("user", "")
        if not user: return redirect(url_for("login"))

        lan = x.default_language = user["user_language"]
        if lan not in x.allowed_languages: lan = "english"
        x.default_language = lan

        return render_template("index.html")
    except Exception as ex:
        ic(ex)
        return "error"

@app.route("/login", methods=["GET", "POST"])
@app.route("/login/<lan>", methods=["GET", "POST"])
def login(lan = "english"):
    try:
        x.site_name = x.lans("log_in")
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

            session["user"] = user

            return f"""<browser mix-redirect="/"></browser>""", 200

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = "error" #should i say system under maintenese? #### TO ASK ####
        if("x exception - " in error_code):
            error_msg = error_code.replace("('x exception - ", "").split("', ")[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>""", 400
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.route("/signup", methods=["GET", "POST"])
@app.route("/signup/<lan>", methods=["GET", "POST"])
def signup(lan = "english"):
    try:
        x.site_name = x.lans("sign_up")
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
            user_password = x.validate_user_password()
            x.validate_user_password_confirm()
            user_username = x.validate_user_username()
            user_first_name = x.validate_user_first_name()
            user_last_name = x.validate_user_last_name()
            current_time = int(time.time())

            encrypted_user_password = generate_password_hash(user_password)

            db, cursor = x.db()
            db.start_transaction()

            q = "INSERT INTO users (user_first_name, user_last_name, user_username, user_email, user_password, user_language, user_created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            
            cursor.execute(q, ( user_first_name, user_last_name, user_username, user_email, encrypted_user_password, x.default_language, current_time))            
            
            user_pk = cursor.lastrowid
            user_uuid = uuid.uuid4().hex

            q = "INSERT INTO not_verifyed_accounts VALUES(%s, %s)"
            cursor.execute(q, (user_pk, user_uuid))
            db.commit()

            # send verification email
            email_verify_account = render_template("___email_verify_account.html", user_verification_key=user_uuid)
            x.send_email(user_email, x.lans('verify_your_account'), email_verify_account)
            
            return f"""<browser mix-redirect="/"></browser>""", 200

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()

        error_code = str(ex)
        error_msg = "error"             #should i say system under maintenese? #### TO ASK ####
        if "x exception - " in error_code:
            error_msg = error_code.replace("('x exception - ", "").split("', ")[0]

        if "Duplicate entry" in error_code and "user_username" in error_code:
            error_msg = x.lans("username_allready_in_system")

        if "Duplicate entry" in error_code and "user_email" in error_code:
            error_msg = x.lans("email_allready_in_system")
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/home")
def view_home():
    try:
        x.site_name = x.lans("home")
        site = render_template("main_pages/home.html")
        return f""" <browser mix-replace='#main'> {site} </browser> """
    except Exception as ex:
        ic(ex)
        return "error"
    
@app.get("/profile")
def view_profile():
    try:
        x.site_name = x.lans("profile")
        site = render_template("main_pages/profile.html")
        return f""" <browser mix-replace='#main'> {site} </browser> """
    except Exception as ex:
        ic(ex)
        return "error"

##############################
########## utilities #########
##############################
@app.get("/get-data-from-sheet")
def get_data_from_sheet():
    try:

        # Validate user is admin
        ################
        # if not session.get("user", ""):
        #     return redirect("/login")

        # user_role_number = session.get("user", "")["role_fk"]  # TO ASK is this the correct way to use pk and fk?
        # db, cursor = x.db()
        # q = "SELECT * FROM roles WHERE role_pk = %s"
        # cursor.execute(q, (user_role_number,))
        # user_role = cursor.fetchone()["role_title"]

        # if "admin" not in user_role:
        #     return redirect("/")
        ################
 
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
 
        return f"""
            <h1>Hi admin user</h1>
            <h2> Data has been saved! </h2> 
            {json_data}
        """
    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()
    
@app.get("/verify-account")
def view_verify_account():
    try:
        user_verification_key = x.validate_uuid4_without_dashes()
        user_verified_at = int(time.time())

        db, cursor = x.db()
        db.start_transaction()
        q = "SELECT user_fk FROM not_verifyed_accounts WHERE uuid = %s"
        cursor.execute(q, (user_verification_key,))

        user_fk = cursor.fetchone()["user_fk"]

        q = "DELETE FROM not_verifyed_accounts WHERE uuid = %s"
        cursor.execute(q, (user_verification_key,))

        q = "UPDATE users SET user_varified_at = %s WHERE user_pk = %s" 
        cursor.execute(q, (user_verified_at, user_fk))

        if cursor.rowcount != 1: raise Exception(f"x exception - {x.lans('cannot_verify_user')}", 400)
        db.commit()

        return redirect( url_for('login') )
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()  

        # System or developer error
        return x.lans('cannot_verify_user')

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.route("/forgot_password", methods=["GET", "POST"])
@app.route("/forgot_password/<lan>", methods=["GET", "POST"])
def view_forgot_password(lan = "english"):
    try:
        x.site_name = x.lans("reset_my_password")
        if lan not in x.allowed_languages: lan = "english"
        x.default_language = lan

        if request.method == "GET": 
            return render_template("forgot_password.html")
        
        if request.method == "POST":
            user_email = x.validate_user_email()

            db, cursor = x.db()
            db.start_transaction()

            q = "SELECT * FROM users WHERE user_email = %s"
            cursor.execute(q, (user_email, ))
            user = cursor.fetchone()
            if user is None:
                raise Exception(f"x exception - {x.lans('no_user_found')}", 400)
            
            user_pk = user["user_pk"]
            new_user_uuid = uuid.uuid4().hex

            q = "SELECT 1 FROM not_verifyed_accounts WHERE user_fk = %s"
            cursor.execute(q, (user_pk,))
            exists = cursor.fetchone()


            if exists:
                q = "UPDATE not_verifyed_accounts SET uuid = %s WHERE user_fk = %s"
                cursor.execute(q, (new_user_uuid, user_pk))
            else:
                q = "INSERT INTO not_verifyed_accounts VALUES(%s, %s)"
                cursor.execute(q, (user_pk, new_user_uuid))

                q = "UPDATE users SET user_varified_at = %s WHERE user_pk = %s" 
                cursor.execute(q, (0, user_pk))
                
            db.commit()

            # send reset password
            reset_password = render_template("___email_reset_password.html", user_reset_key=new_user_uuid)
            x.send_email(user_email, x.lans('reset_your_password'), reset_password)

            succes_template = render_template(("global/succes_message.html"), message="Tjeck your email")
            return f"""<browser mix-bottom='#succes_message'>{succes_template}</browser>"""

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()

        error_code = str(ex)
        error_msg = "error" #should i say system under maintenese? #### TO ASK ####
        if("x exception - " in error_code):
            error_msg = error_code.replace("('x exception - ", "").split("', ")[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>""", 40
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.route("/reset_password", methods=["GET", "POST"])
@app.route("/reset_password/<lan>", methods=["GET", "POST"])
def view_reset_password(lan = "english"):
    try:
        x.site_name = x.lans("reset_my_password")
        if lan not in x.allowed_languages: lan = "english"
        x.default_language = lan

        if request.method == "GET":
            user_verification_key = x.validate_uuid4_without_dashes()
            return render_template("reset_password.html", user_verification_key=user_verification_key)
            
        if request.method == "POST":
            user_verification_key = x.validate_uuid4_without_dashes()
            user_verified_at = int(time.time())

            user_password = x.validate_user_password()
            x.validate_user_password_confirm()
            encrypted_user_password = generate_password_hash(user_password)

            db, cursor = x.db()
            db.start_transaction()
            q = "SELECT user_fk FROM not_verifyed_accounts WHERE uuid = %s"
            cursor.execute(q, (user_verification_key,))
            user = cursor.fetchone()

            if user is None:
                raise Exception(f"x exception - {x.lans('cannot_verify_user')}", 400)
            
            user_fk = user["user_fk"]

            q = "DELETE FROM not_verifyed_accounts WHERE uuid = %s"
            cursor.execute(q, (user_verification_key,))

            q = "UPDATE users SET user_varified_at = %s, user_password = %s WHERE user_pk = %s" 
            cursor.execute(q, (user_verified_at, encrypted_user_password, user_fk))

            if cursor.rowcount != 1: raise Exception(f"x exception - {x.lans('cannot_verify_user')}", 400)
            db.commit()

            return f"""<browser mix-redirect="/login"></browser>""", 200

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        if "db" in locals(): db.rollback()  
        error_msg = "error" #should i say system under maintenese? #### TO ASK ####
        if("x exception - " in error_code):
            error_msg = error_code.replace("('x exception - ", "").split("', ")[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>""", 40
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()