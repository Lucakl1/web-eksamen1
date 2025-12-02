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
        session["current_post_number"] = 0
        user = session.get("user", "")
        if not user: return redirect(url_for("login"))
        user_pk = user["user_pk"]

        lan = x.default_language = user["user_language"]
        if lan not in x.allowed_languages: lan = "english"
        x.default_language = lan

        db, cursor = x.db()

        cursor.execute("SELECT COUNT(*) FROM posts WHERE post_deleted_at = 0")
        count = cursor.fetchone()["COUNT(*)"]
        session["max_number_of_posts"] = int(count)     
        
        posts = x.get_posts(db, cursor, user)

        q = """SELECT 
        user_pk, user_username, user_avatar, user_first_name, user_last_name, user_username 
        FROM users 
        LEFT JOIN followers ON users.user_pk = followers.user_follows_fk 
        WHERE users.user_pk != %s 
        AND (followers.user_fk IS NULL OR followers.user_fk != %s)
        AND user_deleted_at = 0
        ORDER BY RAND() LIMIT 5"""
        cursor.execute(q, (user_pk, user_pk))
        recommended_users = cursor.fetchall()

        for rec_user in recommended_users:
            q = "SELECT * FROM followers WHERE user_fk = %s AND user_follows_fk = %s"
            cursor.execute(q, (user_pk, rec_user["user_pk"]))
            current_user_is_following = cursor.fetchone()

            rec_user["current_user_is_following"] = current_user_is_following

        return render_template("index.html", posts=posts, recommended_users=recommended_users)
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/home")
def view_home():
    try:
        user = session.get("user", "")
        session["current_post_number"] = 0

        db, cursor = x.db()

        cursor.execute("SELECT COUNT(*) FROM posts WHERE post_deleted_at = 0")
        count = cursor.fetchone()["COUNT(*)"]
        session["max_number_of_posts"] = int(count) 

        posts = x.get_posts(db, cursor, user)
        
        site = render_template("main_pages/home.html", posts=posts)
        return f""" 
        <browser mix-replace='#main'> {site} </browser> 
        {x.page_title(x.lans("home"))}
        """
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/explore")
def view_explore():
    try:
        site = render_template("main_pages/explore.html", currently_selectet='users')
        return f""" 
        <browser mix-replace='#main'> {site} </browser> 
        {x.page_title(x.lans("explore"))}
        """
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        pass

@app.get("/profile")
@app.get("/profile/<user_username>")
def view_profile(user_username = ""):
    try:
        user = session.get("user", "")
        session["current_post_number"] = 0
        if not user_username: user_username = user['user_username']

        db, cursor = x.db()
        
        cursor.execute("SELECT COUNT(*) as total FROM posts JOIN users ON user_pk = user_fk WHERE post_deleted_at = 0 AND user_username = %s", (user_username,))
        count = cursor.fetchone()["total"]
        session["max_number_of_posts"] = int(count)
        
        posts = x.get_posts(db, cursor, user, "profile", user_username)

        q = "SELECT * FROM users WHERE user_username = %s"
        cursor.execute(q, (user_username,))
        view_user = cursor.fetchone()

        q = "SELECT * FROM followers WHERE user_fk = %s AND user_follows_fk = %s"
        cursor.execute(q, (user["user_pk"], view_user["user_pk"]))
        current_user_is_following = cursor.fetchone()

        view_user["current_user_is_following"] = current_user_is_following

        site = render_template("main_pages/profile.html", posts=posts, userprofile=view_user, count=count)
        return f""" 
            <browser mix-replace='#main'> {site} </browser> 
            {x.page_title( x.lans('profile') + " - " + user_username )} 
        """
    except Exception as ex:
        ic(ex)
        error_msg = x.lans('system_under_maintenance')
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/followers")
@app.get("/followers/<userprofile>")
def view_followers(userprofile = ""):
    try:
        if userprofile == "": userprofile = session.get("user")["user_username"]

        db, cursor = x.db()
        cursor.execute("SELECT user_pk FROM users WHERE user_username = %s", (userprofile,))
        userprofile_user_pk = cursor.fetchone()

        q = "SELECT * FROM users JOIN followers ON user_fk = user_pk WHERE user_follows_fk = %s"
        cursor.execute(q, (userprofile_user_pk["user_pk"],))
        userprofile_data = cursor.fetchall()

        html_content_followers = render_template("main_pages/followers_following.html", users=userprofile_data)
        return f"""
        <browser mix-replace="#main"> {html_content_followers} </browser> 
        {x.page_title( x.lans('followers') + " - " + userprofile )}
        """

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/following")
@app.get("/following/<userprofile>")
def view_following(userprofile = ""):
    try:
        if userprofile == "": userprofile = session.get("user")["user_username"]

        db, cursor = x.db()
        cursor.execute("SELECT user_pk FROM users WHERE user_username = %s", (userprofile,))
        userprofile_user_pk = cursor.fetchone()

        q = "SELECT * FROM users JOIN followers ON user_follows_fk = user_pk WHERE user_fk = %s"
        cursor.execute(q, (userprofile_user_pk["user_pk"],))
        userprofile_data = cursor.fetchall()

        html_content_followers = render_template("main_pages/followers_following.html", users=userprofile_data)
        return f"""
        <browser mix-replace="#main"> {html_content_followers} </browser> 
        {x.page_title( x.lans('following') + " - " + userprofile )}
        """

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.route("/edit_profile", methods=["GET", "POST"])
def view_edit_profile():
    try:
        if request.method == "GET": 
            user_username = session.get("user", "")["user_username"]
            site = render_template("main_pages/edit_profile.html")
            return f""" 
                <browser mix-replace='#main'> {site} </browser>
                {x.page_title( x.lans('edit_profile') + " - " + user_username )} 
            """
        
        if request.method == "POST":
            user = session.get("user", "")
            user_avatar = x.validate_user_avatar()
            user_banner = x.validate_user_banner()
            user_username = x.validate_user_username()
            user_first_name = x.validate_user_first_name()
            user_last_name = x.validate_user_last_name()
            user_bio = x.validate_user_bio()
            current_time = int(time.time())

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
            q = "UPDATE users SET user_avatar = %s, user_banner = %s, user_username = %s, user_first_name = %s, user_last_name = %s, user_bio = %s, user_updated_at = %s WHERE user_pk = %s"
            cursor.execute(q, (user_avatar, user_banner, user_username, user_first_name, user_last_name, user_bio, current_time, user['user_pk']))
            db.commit()

            session["user"]["user_avatar"] = user_avatar
            session["user"]["user_banner"] = user_banner
            session["user"]["user_username"] = user_username
            session["user"]["user_first_name"] = user_first_name
            session["user"]["user_last_name"] = user_last_name
            session["user"]["user_bio"] = user_bio


            succes_template = render_template(("global/succes_message.html"), message=x.lans("succes"))
            profile_tag = render_template(("___profile_tag.html"))

            cursor.execute("SELECT COUNT(*) as total FROM posts JOIN users ON user_pk = user_fk WHERE post_deleted_at = 0 AND user_username = %s", (user_username,))
            count = cursor.fetchone()["total"]
            session["max_number_of_posts"] = int(count)

            html_content_profile = render_template(("main_pages/profile.html"), userprofile=user, count=count)
            return f"""
                <browser mix-bottom='#succes_message'>{succes_template}</browser>
                <browser mix-replace='#profile_tag'>{profile_tag}</browser>
                <browser mix-replace='#main'>{html_content_profile}</browser>
            """

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]

        if "Duplicate entry" in error_code:
            error_msg = x.lans("username_allready_in_system")
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/bookmark")
def view_bookmark():
    try:
        user = session.get("user", "")
        session["current_post_number"] = 0

        db, cursor = x.db()

        cursor.execute("SELECT COUNT(*) as total FROM posts JOIN bookmarks ON post_pk = post_fk WHERE post_deleted_at = 0 AND bookmarks.user_fk = %s", (user["user_pk"],))
        count = cursor.fetchone()["total"]
        session["max_number_of_posts"] = int(count)
        
        posts = x.get_posts(db, cursor, user, "bookmark", user["user_pk"])

        site = render_template("main_pages/bookmark.html", posts=posts, count=count)

        return f""" 
            <browser mix-replace='#main'> {site} </browser> 
            {x.page_title( x.lans('bookmarks'))} 
        """
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/notifications")
def view_notifications():
    try:
        user = session.get("user", "")
        session["current_post_number"] = 0

        db, cursor = x.db()

        cursor.execute("SELECT COUNT(*) as total FROM users JOIN posts ON user_pk = user_fk JOIN followers ON user_pk = user_follows_fk WHERE post_deleted_at = 0 AND user_deleted_at = 0")        
        count = cursor.fetchone()["total"]
        session["max_number_of_posts"] = int(count)
        
        posts = x.get_posts(db, cursor, user, "notifications")

        site = render_template("main_pages/notifications.html", posts=posts, count=count)

        return f""" 
            <browser mix-replace='#main'> {site} </browser> 
            {x.page_title( x.lans('notifications'))} 
        """
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
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
                return render_template("main_pages/login.html")
            except Exception as ex:
                ic(ex)
                return x.lans('system_under_maintenance')

        if request.method == "POST":
            user_email_or_username = request.form.get("user_email_username", "").strip()

            if "@" in user_email_or_username:
                user_email = x.validate_user_email(user_email_or_username)
                user_password = x.validate_user_password()

                db, cursor = x.db()
                q = "SELECT * FROM users WHERE user_email = %s AND user_deleted_at = 0"
                cursor.execute(q, (user_email,))
                user = cursor.fetchone()

                if not user: raise Exception(f"x exception - {x.lans('email_or_password_is_wrong')}", 400)

                if not check_password_hash(user["user_password"], user_password):
                    raise Exception(f"x exception - {x.lans('email_or_password_is_wrong')}", 400)

            else:
                user_username = x.validate_user_username(user_email_or_username)
                user_password = x.validate_user_password()

                db, cursor = x.db()
                q = "SELECT * FROM users WHERE user_username = %s AND user_deleted_at = 0"
                cursor.execute(q, (user_username,))
                user = cursor.fetchone()

                if not user: raise Exception(f"x exception - {x.lans('username_or_password_is_wrong')}", 400)

                if not check_password_hash(user["user_password"], user_password):
                    raise Exception(f"x exception - {x.lans('username_or_password_is_wrong')}", 400)
                
                
            if user["user_varified_at"] == 0:
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
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
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
                return render_template("main_pages/signup.html")
            except Exception as ex:
                ic(ex)
                return x.lans('system_under_maintenance')

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
            
            cursor.execute(q, (user_first_name, user_last_name, user_username, user_email, encrypted_user_password, x.default_language, current_time))
            
            user_pk = cursor.lastrowid
            user_uuid = uuid.uuid4().hex

            q = "INSERT INTO not_verifyed_accounts VALUES(%s, %s)"
            cursor.execute(q, (user_pk, user_uuid))

            # send verification email
            email_verify_account = render_template("___email_verify_account.html", user_verification_key=user_uuid)
            x.send_email(user_email, x.lans('verify_your_account'), email_verify_account)
            db.commit()
            
            return f"""<browser mix-redirect="/"></browser>""", 200

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()

        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]

        if "Duplicate entry" in error_code and "user_email" in error_code:
            try:
                q = "SELECT user_deleted_at, user_pk, user_banned_at FROM users LEFT JOIN user_admin_bans ON user_pk = user_fk WHERE user_email = %s"
                cursor.execute(q, (user_email,))
                prev_user = cursor.fetchone()
                user_pk = prev_user['user_pk']

                if prev_user["user_banned_at"]:
                    ic("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    error_msg = x.lans("user_has_been_banned")
                elif prev_user["user_deleted_at"] == 0:
                    error_msg = x.lans("email_allready_in_system")
                else:
                    q = "UPDATE users SET user_first_name = %s, user_last_name = %s, user_username = %s, user_password = %s, user_language = %s, user_created_at = %s, user_deleted_at = 0, user_varified_at = 0 WHERE user_pk = %s"
                    cursor.execute(q, (user_first_name, user_last_name, user_username, encrypted_user_password, x.default_language, current_time, user_pk))            

                    user_uuid = uuid.uuid4().hex

                    q = "INSERT INTO not_verifyed_accounts VALUES(%s, %s)"
                    cursor.execute(q, (user_pk, user_uuid))

                    # send verification email
                    email_verify_account = render_template("___email_re_verify_account.html", user_verification_key=user_uuid)
                    x.send_email(user_email, x.lans('verify_your_account'), email_verify_account)
                    db.commit()

                    return f"""<browser mix-redirect="/"></browser>""", 200

            except Exception as ex:
                ic(ex)
                if "db" in locals(): db.rollback()
                error_msg = x.lans("email_allready_in_system")

        if "Duplicate entry" in error_code and "user_username" in error_code:
            error_msg = x.lans("username_allready_in_system")
        
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
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
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
            current_time = int(time.time())

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

            q = "UPDATE users SET user_varified_at = %s, user_password = %s, user_updated_at = %s WHERE user_pk = %s" 
            cursor.execute(q, (current_time, encrypted_user_password, current_time, user_fk))

            if cursor.rowcount != 1: raise Exception(f"x exception - {x.lans('cannot_verify_user')}", 400)
            db.commit()

            html_content_login = render_template("main_pages/login.html")
            succes_template = render_template(("global/succes_message.html"), message=f"{x.lans('password_reset')}")

            return f"""
                <browser mix-replace="main">{html_content_login}</browser>
                <browser mix-bottom='#succes_message'>{succes_template}</browser>
            """

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        if "db" in locals(): db.rollback()  
        error_msg = x.lans('system_under_maintenance')
        if("x exception - " in error_code):
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>""", 400
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
######### Minor calls ########
##############################

@app.get("/delete_profile")
def api_delete_profile():
    try:
        user_username = request.args.get("user", "")
        return f""" 
            <browser mix-replace="#delete_account">  
                <a class="secoundary_button red_button" mix-delete href="/delete_profile_confirm?user={user_username}">{ x.lans('are_you_sure_click_again') }</a>
            </browser>
        """
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')

@app.delete("/delete_profile_confirm")
def api_delete_profile_confirm():
    try:
        user = session.get("user", "")
        user_username = request.args.get("user", "")
        current_time = int(time.time())

        db, cursor = x.db()
        if user_username != user["user_username"]:
            if "admin" in user['user_role']:
                cursor.execute("SELECT user_email, user_first_name, user_last_name, user_pk FROM users WHERE user_username = %s", (user_username,))
                user = cursor.fetchone()

                delete_account_template = render_template("___email_account_deleted.html", user=user)

                q = "UPDATE users SET user_deleted_at = %s WHERE user_username = %s"
                cursor.execute(q, (current_time, user_username))

                q = "INSERT into user_admin_bans (user_fk, user_banned_at) VALUES(%s, %s)"
                cursor.execute(q, (user["user_pk"], current_time))
                db.commit()

                x.send_email(user['user_email'], f"{x.lans('your_account_has_been_banned')}", delete_account_template)
            
                succes_template = render_template(("global/succes_message.html"), message=x.lans("succes"))
                return f""" 
                    <browser mix-bottom='#succes_message'>{succes_template}</browser>
                    <browser mix-redirect="/"></browser>
                """
            
            else:
                raise Exception(f"x exception - {x.lans('you_dont_have_the_authority_to_delete_this_account')}", 400)

        q = "UPDATE users SET user_deleted_at = %s WHERE user_username = %s"
        cursor.execute(q, (current_time, user_username))
        db.commit()
        
        return """<browser mix-redirect="/logout"></browser>"""

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/unban")
def api_unban():
    try:
        user = session.get("user", "")
        user_username = request.args.get("user", "")

        if "admin" in user['user_role']:
            db, cursor = x.db()
            
            db.start_transaction()
            q = "UPDATE users SET user_deleted_at = %s WHERE user_username = %s"
            cursor.execute(q, (0, user_username))

            q = "DELETE FROM user_admin_bans WHERE user_fk = (SELECT user_pk FROM users WHERE user_username = %s)"
            cursor.execute(q, (user_username,))
            db.commit()

            q = "SELECT * FROM users WHERE user_username = %s"
            cursor.execute(q, (user_username,))
            unbanned_user = cursor.fetchone()
            
            x.default_language = unbanned_user["user_language"]
            html_content_unban_account_template = render_template("___email_account_unbanned.html", user=unbanned_user)
            x.send_email(unbanned_user['user_email'], f"{x.lans('your_account_has_been_unbanned')}", html_content_unban_account_template)
            x.default_language = user["user_language"]
        
            cursor.execute("SELECT COUNT(*) as total FROM posts JOIN users ON user_pk = user_fk WHERE post_deleted_at = 0 AND user_username = %s", (user_username,))
            count = cursor.fetchone()["total"]
            session["max_number_of_posts"] = int(count)

            succes_template = render_template(("global/succes_message.html"), message=x.lans("succes"))
            html_content_user_profile = render_template("main_pages/profile.html", userprofile=unbanned_user, count=count)
            return f"""
            <browser mix-replace="#main">{html_content_user_profile}</browser>
            <browser mix-bottom='#succes_message'>{succes_template}</browser>
            """
    
        error_template = render_template(("global/error_message.html"), message=x.lans("you_are_not_an_admin"))
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/follow")
def api_follow():
    try:
        user = session.get("user", "")
        user_username = request.args.get("user", "")

        db, cursor = x.db()
        q = "SELECT user_pk FROM users WHERE user_username = %s"
        cursor.execute(q, (user_username,))
        user_pk = cursor.fetchone()["user_pk"]

        if user_pk == user["user_pk"]: raise Exception(f"x exception - {x.lans('you_cant_follow_yourself')}", 400)
            
        q = "SELECT * FROM followers WHERE user_fk = %s AND user_follows_fk = %s"
        cursor.execute(q, (user["user_pk"], user_pk))
        current_user_is_following = cursor.fetchone()

        if current_user_is_following:
            q = "DELETE FROM followers WHERE user_fk = %s AND user_follows_fk = %s"
            cursor.execute(q, (user["user_pk"], user_pk))
            current_user_is_following = None
        else:
            current_time = int(time.time())
            q = "INSERT INTO followers VALUES(%s, %s, %s)"
            cursor.execute(q, (user["user_pk"], user_pk, current_time))
            current_user_is_following = " "
        db.commit()

        userprofile = {"user_username": user_username}
        userprofile["current_user_is_following"] = current_user_is_following

        follow_button = render_template("___profile_follow_button.html", userprofile=userprofile)
        return f""" <browser mix-replace="#follow{userprofile["user_username"]}"> {follow_button} </browser> """

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.patch("/like_post")
def api_like_post():
    try:
        user_pk = session.get("user", "")["user_pk"]
        post_pk = int(request.args.get("post"))

        db, cursor = x.db()

        q = "SELECT * FROM likes WHERE user_fk = %s AND post_fk = %s"
        cursor.execute(q, (user_pk, post_pk))
        existing_like = cursor.fetchone()

        if existing_like:
            q = "DELETE FROM likes WHERE user_fk = %s AND post_fk = %s"
            existing_like = False
        else:
            q = "INSERT INTO likes VALUES(%s, %s)"
            existing_like = True

        cursor.execute(q, (user_pk, post_pk))
        db.commit()

        q = "SELECT post_total_likes FROM posts WHERE post_pk = %s"
        cursor.execute(q, (post_pk,))
        post_info = cursor.fetchone()

        post = {"post_total_likes": post_info["post_total_likes"], "post_pk": post_pk, "user_has_liked": existing_like}
        like_template = render_template("___post_like.html", post=post)

        return f"""
            <browser mix-replace='#like_post{post_pk}'>
                {like_template}
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

@app.patch("/bookmark_post")
def api_bookmark_post():
    try:
        user_pk = session.get("user", "")["user_pk"]
        post_pk = int(request.args.get("post"))
        current_time = int(time.time())

        db, cursor = x.db()

        q = "SELECT * FROM bookmarks WHERE user_fk = %s AND post_fk = %s"
        cursor.execute(q, (user_pk, post_pk))
        existing_bookmark = cursor.fetchone()

        if existing_bookmark:
            q = "DELETE FROM bookmarks WHERE user_fk = %s AND post_fk = %s"
            existing_bookmark = False
            cursor.execute(q, (user_pk, post_pk))
        else:
            q = "INSERT INTO bookmarks VALUES(%s, %s, %s)"
            existing_bookmark = True
            cursor.execute(q, (user_pk, post_pk, current_time))

        db.commit()

        q = "SELECT post_total_bookmark FROM posts WHERE post_pk = %s"
        cursor.execute(q, (post_pk,))
        post_info = cursor.fetchone()

        post = {"post_total_bookmark": post_info["post_total_bookmark"], "post_pk": post_pk, "user_has_bookmarked": existing_bookmark}
        bookmark_template = render_template("___post_bookmark.html", post=post)

        return f"""
            <browser mix-replace='#bookmark_post{post_pk}'>
                {bookmark_template}
            </browser>
        """
    
    except Exception as ex:
        ic(ex)
        error_msg = {x.lans('something_happened_and_your_bookmark_did_not_get_saved')}
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

@app.post("/make_a_post")
def api_make_a_post():
    try:
        user = session.get("user", "")
        post_message = x.validate_post_message()
        post_media = x.validate_post_media()
        current_time = int(time.time())

        db, cursor = x.db()
        db.start_transaction()
        q = "INSERT INTO posts (user_fk, post_message, post_created_at) VALUES (%s, %s, %s)"
        cursor.execute(q, (user['user_pk'], post_message, current_time))
        post_pk = cursor.lastrowid

        if post_media != "":
            ext = post_media.filename.rsplit(".", 1)[-1].lower()
            post_media.save(os.path.join(x.upload_folder_path, post_media.filename))
            post_media = post_media.filename

            if ext in {"jpg", "jpeg", "png", "webp"}:
                category = "image"
            elif ext in {"mp4"}:
                category = "video"
            elif ext in {"mp3"}:
                category = "audio"
            elif ext in {"pdf", "txt"}:
                category = "file"

            q = "SELECT post_media_type_pk FROM post_media_types WHERE post_media_type_type = %s"
            cursor.execute(q, (category,))
            post_media_type_pk = cursor.fetchone()["post_media_type_pk"]

            q = "INSERT INTO post_medias (post_fk, post_media_path, post_media_type_fk) VALUES (%s, %s, %s)"
            cursor.execute(q, (post_pk, post_media, post_media_type_pk))

        db.commit()

        if post_media != "":
            q = "SELECT * FROM posts JOIN post_medias ON post_pk = post_fk WHERE post_pk = %s"
            cursor.execute(q, (post_pk,))
            post = cursor.fetchone()

            q = "SELECT post_media_type_type FROM post_media_types WHERE post_media_type_pk = %s"
            cursor.execute(q, (post["post_media_type_fk"],))
            post_media_type = cursor.fetchone()
        else:
            q = "SELECT * FROM posts WHERE post_pk = %s"
            cursor.execute(q, (post_pk,))
            post = cursor.fetchone()

        post["user_username"] = user["user_username"]
        post["user_banner"] = user["user_banner"]
        post["user_avatar"] = user["user_avatar"]
        post["user_first_name"] = user["user_first_name"]
        post["user_last_name"] = user["user_last_name"]
        post["user_created_at"] = user["user_created_at"]
        post["user_bio"] = user["user_bio"]
        post["user_pk"] = user["user_pk"]
        if post_media != "": post["post_media_type"] = post_media_type["post_media_type_type"]

        html_content_post = render_template("_post.html", post=post)
        html_content_home_post_form = render_template("___home_post_form.html", post=post)
        succes_template = render_template(("global/succes_message.html"), message=x.lans("succes"))
        
        return f"""
            <browser mix-top='#posts'>{html_content_post}</browser>
            <browser mix-replace='#make_a_post'>{html_content_home_post_form}</browser>
            <browser mix-bottom='#succes_message'>{succes_template}</browser>
        """
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close() 

@app.route("/edit_post", methods=["GET", "POST"])
def api_edit_post():
    try:
        user = session.get("user", "")
        post_pk = request.args.get("post", "")
        if post_pk == "": raise Exception(f"x exception - {x.lans('post_is_deleted')}", 400)
        db, cursor = x.db()

        q = "SELECT * FROM posts JOIN users ON user_pk = user_fk WHERE post_pk = %s"
        cursor.execute(q, (post_pk,))
        post = cursor.fetchone()
        db.commit()

        if post["user_fk"] != user["user_pk"]:
            raise Exception(f"x exception - {x.lans('you_dont_have_the_authority_to_edit_this_post')}", 400)
        
        if request.method == "GET":
                
            edit_post_template = render_template(("_edit_post.html"), post=post)
            return f"""
                <browser mix-replace='#post{post_pk}'>{edit_post_template}</browser>
            """
        
        if request.method == "POST":
            current_time = int(time.time())
            new_post_message = x.validate_post_message()
            remove_media = request.form.get("delete_media", "")

            db.start_transaction()
            q = "UPDATE posts SET post_message = %s, post_updated_at = %s WHERE post_pk = %s"
            cursor.execute(q, (new_post_message, current_time, post_pk))

            category = ""
            if remove_media == "on":
                q = "DELETE FROM post_medias WHERE post_fk = %s"
                cursor.execute(q, (post_pk,))
            else:
                new_post_media = x.validate_post_media()
                
                if new_post_media != "":
                    ext = new_post_media.filename.rsplit(".", 1)[-1].lower()
                    new_post_media.save(os.path.join(x.upload_folder_path, new_post_media.filename))
                    new_post_media = new_post_media.filename

                    if ext in {"jpg", "jpeg", "png", "webp"}:
                        category = "image"
                    elif ext in {"mp4"}:
                        category = "video"
                    elif ext in {"mp3"}:
                        category = "audio"
                    elif ext in {"pdf", "txt"}:
                        category = "file"

                    q = "SELECT post_media_type_pk FROM post_media_types WHERE post_media_type_type = %s"
                    cursor.execute(q, (category,))
                    post_media_type_pk = cursor.fetchone()["post_media_type_pk"]

                    q = "SELECT * FROM post_medias WHERE post_fk = %s"
                    cursor.execute(q, (post_pk,))
                    media_allready_exists = cursor.fetchone()

                    if media_allready_exists:
                        q = "UPDATE post_medias SET post_media_path = %s, post_media_type_fk = %s WHERE post_fk = %s"
                        cursor.execute(q, (new_post_media, post_media_type_pk, post_pk))
                    else:
                        q = "INSERT INTO post_medias (post_fk, post_media_path, post_media_type_fk) VALUES (%s, %s, %s)"
                        cursor.execute(q, (post_pk, new_post_media, post_media_type_pk))
            db.commit()

            q = """
            SELECT 
            post_pk, post_created_at, post_deleted_at, post_message, post_pk, post_total_comments, post_total_likes, post_total_bookmark, post_updated_at,
            user_avatar, user_banner, user_bio, user_first_name, user_last_name, user_username, user_pk, user_created_at,
            post_media_type_fk, post_media_path
            FROM users 
            JOIN posts ON user_pk = user_fk
            LEFT JOIN post_medias ON post_pk = post_fk
            WHERE post_deleted_at = 0 AND post_pk = %s
            """
            cursor.execute(q, (post_pk,))
            post = cursor.fetchone()
            
            if category != "": post["post_media_type"] = category

            q = "SELECT * FROM likes WHERE user_fk = %s AND post_fk = %s"
            cursor.execute(q, (user["user_pk"], post_pk))
            existing_like = cursor.fetchone()
            
            q = "SELECT * FROM bookmarks WHERE user_fk = %s AND post_fk = %s"
            cursor.execute(q, (user["user_pk"], post_pk))
            existing_bookmark = cursor.fetchone()

            post["user_has_liked"] = existing_like
            post["user_has_bookmarked"] = existing_bookmark
            

            new_post = render_template("_post.html", post=post)
            succes_template = render_template(("global/succes_message.html"), message=x.lans("post_updated"))
            return f""" 
                <browser mix-replace="#post{post_pk}"> {new_post} </browser>
                <browser mix-bottom='#succes_message'>{succes_template}</browser>
            """

    except Exception as ex:
        if "db" in locals(): db.rollback()
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.delete("/delete_post")
def api_delete_post():
    try:
        user = session.get("user", "")
        post_pk = request.args.get("post", "")
        current_time = int(time.time())
        if post_pk == "": raise Exception(f"x exception - {x.lans('post_is_allready_deleted')}", 400)

        db, cursor = x.db()

        q = "SELECT * FROM posts WHERE post_pk = %s"
        cursor.execute(q, (post_pk,))
        post = cursor.fetchone()

        if post["user_fk"] != user["user_pk"]:
            if "admin" in user['user_role']:
                q = "SELECT user_first_name, user_last_name, user_language, post_message FROM posts JOIN users ON user_pk = user_fk WHERE post_pk = %s"
                cursor.execute(q, (post_pk,))
                post = cursor.fetchone()

                x.default_language = post["user_language"]
                message_to_user = render_template("___email_post_deleted.html", post=post)
                x.send_email(post["user_email"], x.lans("one_of_your_post_has_been_deleted"), message_to_user)
                x.default_language = user["user_language"]
            else:
                raise Exception(f"x exception - {x.lans('you_dont_have_the_authority_to_delete_this_post')}", 400)            
        
        q = "UPDATE posts SET post_deleted_at = %s WHERE post_pk = %s"
        cursor.execute(q, (current_time, post_pk))
        db.commit()
            
        succes_template = render_template(("global/succes_message.html"), message=x.lans("post_deleted"))
        return f"""
            <browser mix-bottom='#succes_message'>{succes_template}</browser>
            <browser mix-remove='#post{post_pk}'></browser>
        """
    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.route("/comments", methods=["GET", "POST"])
def api_comments():
    try:
        post_pk = request.args.get("post", "")
        db, cursor = x.db()

        if request.method == "GET":
            q = "SELECT * FROM comments JOIN users ON user_fk = user_pk WHERE post_fk = %s ORDER BY comment_created_at DESC LIMIT 5"
            cursor.execute(q, (post_pk,))
            comments = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) as total FROM comments WHERE post_fk = %s", (post_pk,))
            count = int(cursor.fetchone()["total"])

            template_comments = render_template("_append_comments.html", comments=comments, post_pk=post_pk, count=count)

            return f"""<browser mix-replace="#comments{post_pk}"> {template_comments} </browser>"""
        
        if request.method == "POST":
            user = session.get("user", "")
            user_pk = user["user_pk"]
            comment_message = x.validate_comment_message()
            current_time = int(time.time())

            q = "INSERT INTO comments (post_fk, user_fk, comment_message, comment_created_at) VALUES(%s, %s, %s, %s)"
            cursor.execute(q, (post_pk, user_pk, comment_message, current_time))
            db.commit()
            comment_pk = cursor.lastrowid

            q = "SELECT post_pk, post_total_comments FROM posts WHERE post_pk = %s"
            cursor.execute(q, (post_pk,))
            post = cursor.fetchone()

            comment = {}
            comment["comment_pk"] = comment_pk
            comment["post_fk"] = post_pk
            comment["user_fk"] = user_pk
            comment["comment_message"] = comment_message
            comment["comment_created_at"] = current_time
            comment["comment_updated_at"] = 0

            comment["user_username"] = user["user_username"]
            comment["user_banner"] = user["user_banner"]
            comment["user_avatar"] = user["user_avatar"]
            comment["user_first_name"] = user["user_first_name"]
            comment["user_last_name"] = user["user_last_name"]
            comment["user_created_at"] = user["user_created_at"]
            comment["user_bio"] = user["user_bio"]
            
            comment_template = render_template("_comment.html", comment=comment)
            comment_count_template = render_template("___post_comment.html", post=post)
            succes_template = render_template(("global/succes_message.html"), message=x.lans("succes"))
            post_comment_form = render_template(("___post_comment_form.html"), post_pk=post_pk)

            return f""" 
                <browser mix-top="#all_comments{post_pk}">{comment_template}</browser> 
                <browser mix-replace="#comment_count{post_pk}">{comment_count_template}</browser>
                <browser mix-bottom='#succes_message'>{succes_template}</browser>
                <browser mix-replace='#comments_form{post_pk}'>{post_comment_form}</browser>
            """

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.route("/edit_comment", methods=["GET", "POST"])
def api_edit_comment():
    try:
        user = session.get("user", "")
        comment_pk = request.args.get("comment", "")
        if comment_pk == "": raise Exception(f"x exception - {x.lans('comment_is_deleted')}", 400)
        db, cursor = x.db()

        q = "SELECT * FROM comments JOIN users ON user_pk = user_fk WHERE comment_pk = %s"
        cursor.execute(q, (comment_pk,))
        comment = cursor.fetchone()
        db.commit()

        if comment["user_fk"] != user["user_pk"]:
            raise Exception(f"x exception - {x.lans('you_dont_have_the_authority_to_edit_this_comment')}", 400)
        
        if request.method == "GET":
                
            edit_comment_template = render_template(("_edit_comment.html"), comment=comment)
            return f"""
                <browser mix-replace='#comment{comment_pk}'>{edit_comment_template}</browser>
            """
        
        if request.method == "POST":
            comment_message = x.validate_comment_message()
            current_time = int(time.time())


            q = "UPDATE comments SET comment_message = %s, comment_updated_at = %s WHERE comment_pk = %s"
            cursor.execute(q, (comment_message, current_time, comment_pk))

            comment = {}
            comment["comment_pk"] = comment_pk
            comment["user_fk"] = user["user_pk"]
            comment["comment_message"] = comment_message
            comment["comment_updated_at"] = current_time
            comment["comment_created_at"] = 0

            comment["user_username"] = user["user_username"]
            comment["user_banner"] = user["user_banner"]
            comment["user_avatar"] = user["user_avatar"]
            comment["user_first_name"] = user["user_first_name"]
            comment["user_last_name"] = user["user_last_name"]
            comment["user_created_at"] = user["user_created_at"]
            comment["user_bio"] = user["user_bio"]
            
            comment_template = render_template("_comment.html", comment=comment)
            succes_template = render_template(("global/succes_message.html"), message=x.lans("succes"))

            return f""" 
                <browser mix-replace="#comment{comment_pk}"> {comment_template} </browser> 
                <browser mix-bottom='#succes_message'>{succes_template}</browser>
            """


    except Exception as ex:
        if "db" in locals(): db.rollback()
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.delete("/delete_comment")
def api_delete_comment():
    try:
        user = session.get("user", "")
        comment_pk = request.args.get("comment", "")
        if comment_pk == "": raise Exception(f"x exception - {x.lans('comment_is_allready_deleted')}", 400)

        db, cursor = x.db()

        q = "SELECT * FROM comments WHERE comment_pk = %s"
        cursor.execute(q, (comment_pk,))
        comment = cursor.fetchone()

        if comment["user_fk"] != user["user_pk"]:
            if "admin" in user['user_role']:
                q = "SELECT * FROM posts JOIN users ON user_pk = user_fk WHERE comment_pk = %s"
                cursor.execute(q, (comment_pk,))
                comment = cursor.fetchone()

                x.default_language = comment["user_language"]
                message_to_user = render_template("___email_comment_deleted.html", comment=comment)
                x.send_email(comment["user_email"], x.lans("one_of_your_comment_has_been_deleted"), message_to_user)
                x.default_language = user["user_language"]
            else:
                raise Exception(f"x exception - {x.lans('you_dont_have_the_authority_to_delete_this_comment')}", 400)            
        
        q = "SELECT post_pk, post_total_comments FROM posts WHERE post_pk = (SELECT post_fk FROM comments WHERE comment_pk = %s)"
        cursor.execute(q, (comment_pk,))
        post = cursor.fetchone()

        q = "DELETE FROM comments WHERE comment_pk = %s"
        cursor.execute(q, (comment_pk,))
        db.commit()

        post["post_total_comments"] = post["post_total_comments"] - 1
            
        comment_count_template = render_template("___post_comment.html", post=post)
        succes_template = render_template(("global/succes_message.html"), message=x.lans("comment_deleted"))
        
        return f"""
            <browser mix-bottom='#succes_message'>{succes_template}</browser>
            <browser mix-remove='#comment{comment_pk}'></browser>
            <browser mix-replace="#comment_count{post["post_pk"]}">{comment_count_template}</browser>
        """
    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/more_comments")
def api_more_comments():
    try:
        post_pk = request.args.get("post", "")
        current_count = int(request.args.get("current_count", ""))
        
        db, cursor = x.db()
        q = "SELECT * FROM comments JOIN users ON user_fk = user_pk WHERE post_fk = %s ORDER BY comment_created_at DESC LIMIT 5 OFFSET %s"
        cursor.execute(q, (post_pk, current_count))
        comments = cursor.fetchall()

        current_count = current_count + 5
        cursor.execute("SELECT COUNT(*) as total FROM comments WHERE post_fk = %s", (post_pk,))
        total_amount_of_comments = int(cursor.fetchone()["total"])


        template_comments = render_template("___append_more_comments.html", comments=comments, post_pk=post_pk, current_count=current_count, total_amount_of_comments=total_amount_of_comments)

        return f"""
            <browser mix-replace="#more_comments_button{post_pk}">{template_comments}<browser>
        """

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.post("/aside_user_search")
def api_aside_user_search():
    try:
        user = session.get("user", "")
        user_pk = user["user_pk"]
        user_search = f"{request.form.get('user_name_search', '')}%"

        recommended_users = ""
        if user_search != "%":
            db, cursor = x.db()
            q = """SELECT 
            user_pk, user_username, user_avatar, user_first_name, user_last_name, user_username 
            FROM users 
            LEFT JOIN followers ON users.user_pk = followers.user_follows_fk 
            WHERE users.user_pk != %s
            AND (user_username LIKE %s OR user_first_name LIKE %s OR user_last_name LIKE %s)
            AND user_deleted_at = 0
            LIMIT 7"""
            cursor.execute(q, (user_pk, user_search, user_search, user_search))
            recommended_users = cursor.fetchall()

            for rec_user in recommended_users:
                q = "SELECT * FROM followers WHERE user_fk = %s AND user_follows_fk = %s"
                cursor.execute(q, (user_pk, rec_user["user_pk"]))
                current_user_is_following = cursor.fetchone()

                rec_user["current_user_is_following"] = current_user_is_following

        recommended_users_template = f"<div id='search_results' class='recommended_users'> {render_template('___recommended_users.html', recommended_users=recommended_users)} </div>"

        return f"""<browser mix-replace="#search_results"> {recommended_users_template} </browser>"""
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/change_search_for")
@app.get("/change_search_for/<search_fore>")
def api_change_search_for(search_fore = "users"):
    try:
        change_search_for = render_template("_change_search_for.html", currently_selectet=search_fore)
        return f"""<browser mix-replace="#search_selector"> {change_search_for} </browser>"""
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    
@app.post("/make_a_search_request")
def api_make_a_search_request():
    try:
        user = session.get("user", "")
        user_pk = user["user_pk"]
        search_value = request.form.get('search_for_value', '')
        search_for = request.form.get('search_for', '')

        db, cursor = x.db()
        if search_for == "users":
            search_value = f"{search_value}%"
            cursor.execute("""SELECT COUNT(*) as total FROM users 
                           WHERE users.user_pk != %s AND (user_username LIKE %s OR user_first_name LIKE %s OR user_last_name LIKE %s) 
                           AND user_deleted_at = 0""", (user_pk, search_value, search_value, search_value))        
            count = int(cursor.fetchone()["total"])
            session["max_number_of_posts"] = int(count)

            q = """SELECT 
            user_pk, user_username, user_avatar, user_first_name, user_last_name, user_username 
            FROM users 
            LEFT JOIN followers ON users.user_pk = followers.user_follows_fk 
            WHERE users.user_pk != %s
            AND (user_username LIKE %s OR user_first_name LIKE %s OR user_last_name LIKE %s)
            AND user_deleted_at = 0
            LIMIT 10"""
            cursor.execute(q, (user_pk, search_value, search_value, search_value))
            users = cursor.fetchall()

            for result_user in users:
                q = "SELECT * FROM followers WHERE user_fk = %s AND user_follows_fk = %s"
                cursor.execute(q, (user_pk, result_user["user_pk"]))
                current_user_is_following = cursor.fetchone()

                result_user["current_user_is_following"] = current_user_is_following

            search_results_template = render_template("___search_users_result.html", users=users, count=count, search_value=search_value)
        
        elif search_for == "posts":

            cursor.execute("""SELECT COUNT(*) as total FROM users JOIN posts ON user_pk = user_fk WHERE post_deleted_at = 0 AND user_deleted_at = 0 AND MATCH(post_message) AGAINST("%s" IN NATURAL LANGUAGE MODE WITH QUERY EXPANSION)""", (search_value,))        
            count = int(cursor.fetchone()["total"])
            posts = x.get_posts(db, cursor, user, "explore", search_value)
            session["max_number_of_posts"] = int(count)
            
            search_results_template = render_template("___search_posts_result.html", posts=posts, count=count, search_value=search_value)

        return f"""<browser mix-replace="#search_content"> 
            <section id="search_content">
                {search_results_template} 
            </section>
        </browser>"""
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/get_more_posts_home")
def api_get_more_posts_home():
    try:
        max_number_of_posts = session.get("max_number_of_posts")
        current_post_number = session.get("current_post_number", 0) + 5
        session["current_post_number"] = current_post_number
        user = session.get("user")

        db, cursor = x.db()
        posts = x.get_posts(db, cursor, user, "home", "", current_post_number)

        remove_more_button = ""
        if max_number_of_posts <= current_post_number + 5: 
            remove_more_button = f"<browser mix-remove='#auto_show_more'></browser>"

        htmlPosts = render_template("___append_more_posts.html", posts=posts)

        return f""" 
            <browser mix-bottom="#posts"> {htmlPosts} </browser>
            {remove_more_button}
        """
    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/get_more_posts_profile")
def api_get_more_posts_profile():
    try:
        max_number_of_posts = session.get("max_number_of_posts")
        current_post_number = session.get("current_post_number", 0) + 5
        session["current_post_number"] = current_post_number
        user = session.get("user")
        user_username = request.args.get("username", user["user_username"])

        db, cursor = x.db()
        posts = x.get_posts(db, cursor, user, "profile", user_username, current_post_number)

        remove_more_button = ""
        if max_number_of_posts <= current_post_number + 5: 
            remove_more_button = f"<browser mix-remove='#auto_show_more'></browser>"

        htmlPosts = render_template("___append_more_posts.html", posts=posts)

        return f""" 
            <browser mix-bottom="#posts"> {htmlPosts} </browser>
            {remove_more_button}
        """
    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close() 

@app.get("/get_more_posts_bookmarked")
def api_get_more_posts_bookmarked():
    try:
        max_number_of_posts = session.get("max_number_of_posts")
        current_post_number = session.get("current_post_number", 0) + 5
        session["current_post_number"] = current_post_number
        user = session.get("user")

        db, cursor = x.db()
        posts = x.get_posts(db, cursor, user, "bookmark", user["user_pk"], current_post_number)

        remove_more_button = ""
        if max_number_of_posts <= current_post_number + 5: 
            remove_more_button = f"<browser mix-remove='#auto_show_more'></browser>"

        htmlPosts = render_template("___append_more_posts.html", posts=posts)

        return f""" 
            <browser mix-bottom="#posts"> {htmlPosts} </browser>
            {remove_more_button}
        """
    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close() 

@app.get("/get_more_posts_notifications")
def api_get_more_posts_notifications():
    try:
        max_number_of_posts = session.get("max_number_of_posts")
        current_post_number = session.get("current_post_number", 0) + 5
        session["current_post_number"] = current_post_number
        user = session.get("user")

        db, cursor = x.db()
        posts = x.get_posts(db, cursor, user, "notifications", None, current_post_number)

        remove_more_button = ""
        if max_number_of_posts <= current_post_number + 5: 
            remove_more_button = f"<browser mix-remove='#auto_show_more'></browser>"

        htmlPosts = render_template("___append_more_posts.html", posts=posts)

        return f""" 
            <browser mix-bottom="#posts"> {htmlPosts} </browser>
            {remove_more_button}
        """
    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/get_more_posts_explore_users")
def api_get_more_posts_explore_users():
    try:
        max_number_of_users = session.get("max_number_of_posts")
        current_user_number = session.get("current_post_number", 0) + 10
        session["current_post_number"] = current_user_number
        search_value = request.args.get("search_value", "")
        user = session.get("user")
        
        db, cursor = x.db()
        q = """SELECT 
            user_pk, user_username, user_avatar, user_first_name, user_last_name, user_username 
            FROM users 
            LEFT JOIN followers ON users.user_pk = followers.user_follows_fk 
            WHERE users.user_pk != %s
            AND (user_username LIKE %s OR user_first_name LIKE %s OR user_last_name LIKE %s)
            AND user_deleted_at = 0
            LIMIT 4
            OFFSET %s"""
        cursor.execute(q, (user["user_pk"], search_value, search_value, search_value, current_user_number))
        users = cursor.fetchall()

        remove_more_button = ""
        if max_number_of_users <= current_user_number + 10: 
            remove_more_button = f"<browser mix-remove='#auto_show_more'></browser>"

        htmlUsers = render_template("___recommended_users.html", recommended_users=users)

        return f""" 
            <browser mix-bottom="#users"> {htmlUsers} </browser>
            {remove_more_button}
        """
    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/get_more_posts_explore_posts")
def api_get_more_posts_explore_posts():
    try:
        max_number_of_posts = session.get("max_number_of_posts")
        current_post_number = session.get("current_post_number", 0) + 5
        session["current_post_number"] = current_post_number
        search_value = request.args.get("search_value", "")
        user = session.get("user")
        
        db, cursor = x.db()
        posts = x.get_posts(db, cursor, user, "explore", search_value, current_post_number)

        remove_more_button = ""
        if max_number_of_posts <= current_post_number + 5: 
            remove_more_button = f"<browser mix-remove='#auto_show_more'></browser>"

        htmlPosts = render_template("___append_more_posts.html", posts=posts)

        return f""" 
            <browser mix-bottom="#posts"> {htmlPosts} </browser>
            {remove_more_button}
        """
    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
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
        user = session.get("user", "")
        if not user:
            return redirect(url_for('login'))

        if "admin" not in user['user_role']:
            return redirect("/")
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

@app.get("/get_admin_all_users")
def get_admin_all_users():
    try:
        # Validate user is admin
        ################
        user = session.get("user", "")
        if not user:
            return redirect(url_for('login'))

        if "admin" not in user['user_role']:
            return redirect("/")
        ################

        db, cursor = x.db()
        q = "SELECT COUNT(*) as total FROM users"
        cursor.execute(q)
        all_user_count = int(cursor.fetchone()["total"])
 
        q = "SELECT * FROM users LIMIT 30"
        cursor.execute(q)
        all_users = cursor.fetchall()


        template_fore_all_users = render_template("_____admin_all_users.html", users=all_users, all_user_count=all_user_count)

        header = render_template("global/header.html")

        return f""" <browser mix-replace="#main">
            <main id="main" class="admin_all_users"> 
                {template_fore_all_users}
            </main>
            </browser>
        """

    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/admin_all_more_users")
def api_admin_all_users():
    try:
        # Validate user is admin
        ################
        user = session.get("user", "")
        if not user:
            return redirect(url_for('login'))

        if "admin" not in user['user_role']:
            return redirect("/")
        ################

        next_users_count = int(request.args.get("current_count", ""))
        total_count = int(request.args.get("total_count", ""))
 
        db, cursor = x.db()
        q = "SELECT * FROM users LIMIT 30 OFFSET %s"
        cursor.execute(q, (next_users_count,))
        all_users = cursor.fetchall()

        template_fore_all_users = render_template("_____admin_more_users.html", users=all_users)

        next_users_count = next_users_count + 30

        remove_more_button = f"""
            <browser mix-replace='#auto_show_more'>
                <button href="/admin_all_more_users?total_count={total_count}&current_count={ next_users_count }" mix-get mix-default="{ x.lans('more_users') }" mix-await="{ x.lans('loading...') }" class="main_button" id="auto_show_more">
                    { x.lans('more_users') }
                </button>
            </browser>"""
        
        if total_count <= next_users_count: 
            remove_more_button = f"<browser mix-remove='#auto_show_more'></browser>"

        return f""" 
            <browser mix-bottom="#users">{template_fore_all_users}</browser>
            {remove_more_button}
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
        db.commit()

        return redirect(url_for('login'))
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()  

        # System or developer error
        return x.lans('cannot_verify_user')

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()