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

        db, cursor = x.db()
        q = """SELECT 
        post_pk, post_created_at, post_deleted_at, post_message, post_pk, post_total_comments, post_total_likes, post_total_saved, 
        post_updated_at, user_avatar, user_banner, user_bio, user_first_name, user_last_name, user_username, user_pk
        FROM users JOIN posts ON user_pk = user_fk WHERE post_deleted_at = 0 ORDER BY RAND() LIMIT 5"""
        cursor.execute(q)
        posts = cursor.fetchall()

        for post in posts:
            user_pk = post['user_pk']
            post_pk = post['post_pk']

            q = "SELECT * FROM likes WHERE user_fk = %s AND post_fk = %s LIMIT 1"
            cursor.execute(q, (user_pk, post_pk))
            liked = cursor.fetchone()

            post['user_has_liked'] = False
            if liked: post['user_has_liked'] = True

        return render_template("index.html", posts=posts)
    except Exception as ex:
        ic(ex)
        return "error"
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/home")
def view_home():
    try:
        x.site_name = x.lans("home")

        db, cursor = x.db()
        q = """SELECT 
        post_pk, post_created_at, post_deleted_at, post_message, post_pk, post_total_comments, post_total_likes, post_total_saved, 
        post_updated_at, user_avatar, user_banner, user_bio, user_first_name, user_last_name, user_username 
        FROM users JOIN posts ON user_pk = user_fk WHERE post_deleted_at = 0 ORDER BY RAND() LIMIT 5"""
        cursor.execute(q)
        posts = cursor.fetchall()
        
        site = render_template("main_pages/home.html", posts=posts)
        return f""" <browser mix-replace='#main'> {site} </browser> """
    except Exception as ex:
        ic(ex)
        return "error"
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

    
@app.get("/profile")
@app.get("/profile/<user_username>")
def view_profile(user_username = ""):
    try:
        x.site_name = f"{x.lans('profile')} {user_username}"
        user = session.get("user", "")
        if not user_username: user_username = user['user_username']

        db, cursor = x.db()
        q = """SELECT 
        post_pk, post_created_at, post_deleted_at, post_message, post_pk, post_total_comments, post_total_likes, post_total_saved, 
        post_updated_at, user_avatar, user_banner, user_bio, user_first_name, user_last_name, user_username 
        FROM users JOIN posts ON user_pk = user_fk WHERE post_deleted_at = 0 AND user_username = %s ORDER BY RAND() LIMIT 5"""
        cursor.execute(q, (user_username,))
        posts = cursor.fetchall()

        q = "SELECT * FROM users WHERE user_username = %s"
        cursor.execute(q, (user_username,))
        user = cursor.fetchone()

        site = render_template("main_pages/profile.html", posts=posts, userprofile=user)
        return f""" <browser mix-replace='#main'> {site} </browser> """
    except Exception as ex:
        ic(ex)
        error_msg = "error"
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.route("/edit_profile", methods=["GET", "POST"])
def view_edit_profile():
    try:
        if request.method == "GET": 
            x.site_name = x.lans("edit_profile")

            site = render_template("main_pages/edit_profile.html")
            return f""" <browser mix-replace='#main'> {site} </browser> """
        
        if request.method == "POST":
            user = session.get("user", "")
            user_avatar = x.validate_user_avatar()
            user_banner = x.validate_user_banner()
            user_username = x.validate_user_username()
            user_first_name = x.validate_user_first_name()
            user_last_name = x.validate_user_last_name()
            user_bio = x.validate_user_bio()

            if user_avatar != "":
                user_avatar.save(os.path.join(x.upload_folder_path, user_avatar.filename))
                user_avatar = user_avatar.filename
            else:
                user_avatar = user['user_avatar']

            if user_banner != "":
                user_banner.save(os.path.join(x.upload_folder_path, user_banner.filename))
                user_banner = user_banner.filename
            else:
                user_banner = user['user_banner']

            db, cursor = x.db()
            q = "UPDATE users SET user_avatar = %s, user_banner = %s, user_username = %s, user_first_name = %s, user_last_name = %s, user_bio = %s WHERE user_pk = %s"
            cursor.execute(q, (user_avatar, user_banner, user_username, user_first_name, user_last_name, user_bio, user['user_pk']))
            db.commit()

            session["user"]["user_avatar"] = user_avatar
            session["user"]["user_banner"] = user_banner
            session["user"]["user_username"] = user_username
            session["user"]["user_first_name"] = user_first_name
            session["user"]["user_last_name"] = user_last_name
            session["user"]["user_bio"] = user_bio


            succes_template = render_template(("global/succes_message.html"), message="succes")
            profile_tag = render_template(("___profile_tag.html"))
            return f"""
                <browser mix-bottom='#succes_message'>{succes_template}</browser>
                <browser mix-replace='#profile_tag'>{profile_tag}</browser>
            """

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split('",')[0]

        if "Duplicate entry" in error_code:
            error_msg = x.lans("username_allready_in_system")
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
#### Login | signup flow #####
##############################

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
            
            q = "SELECT * FROM roles WHERE role_pk = %s"
            cursor.execute(q, (user["role_fk"],))
            user_role = cursor.fetchone()["role_title"]

            user['user_role'] = user_role
            user.pop("user_password")

            session["user"] = user

            return f"""<browser mix-redirect="/"></browser>""", 200

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if("x exception - " in error_code):
            error_msg = error_code.split("x exception - ")[1].split('",')[0]
        
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
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split('",')[0]

        if "Duplicate entry" in error_code and "user_username" in error_code:
            error_msg = x.lans("username_allready_in_system")

        if "Duplicate entry" in error_code and "user_email" in error_code:
            error_msg = x.lans("email_allready_in_system")
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    
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

            succes_template = render_template(("global/succes_message.html"), message=f"{x.lans('tjeck_your_email')}")
            return f"""<browser mix-bottom='#succes_message'>{succes_template}</browser>"""

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()

        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if("x exception - " in error_code):
            error_msg = error_code.split("x exception - ")[1].split('",')[0]
        
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
        error_msg = x.lans('system_under_maintenance')
        if("x exception - " in error_code):
            error_msg = error_code.split("x exception - ")[1].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>""", 400
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
######### Minor calls ########
##############################

@app.patch("/like-post")
def api_like_post():
    try:
        button_unlike_tweet = render_template("___post_unlike.html")

        return f"""
            <browser mix-replace="#button_1">
                {button_unlike_tweet}
            </browser>
        """
    
    except Exception as ex:
        ic(ex)
        error_msg = {x.lans('something_happend_and_like_did_not_get_saved')}
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>""", 400
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close() 

@app.get("/change_lan/<lan>")
def api_change_lan(lan = "english"):
    try:
        if lan not in x.allowed_languages: lan = "english"

        user = session.get("user", "")
        if lan in user['user_language']:
            return redirect("/")

        db, cursor = x.db()
        q = "UPDATE users SET user_language = %s WHERE user_pk = %s"
        cursor.execute(q, (lan, user['user_pk']))
        db.commit()

        session["user"]["user_language"] = lan

        return redirect("/")
    
    except Exception as ex:
        ic(ex)
        return {x.lans('system_under_maintenance')}, 400
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close() 

##############################
########## utilities #########
##############################
@app.get("/get-data-from-sheet")
def get_data_from_sheet():
    try:

        # Validate user is admin
        ################
        # user = session.get("user", "")
        # if not user:
        #     return redirect("/login")

        # if "admin" not in user['user_role']:
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

        header = render_template("global/header.html")
 
        return f""" 
            {header}
            <main class="dictionary"> 
                <h1>Hi admin user</h1>
                <h2> Data has been saved! </h2>
                <br>
                {json_data}
            </main>
            </body></html>
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