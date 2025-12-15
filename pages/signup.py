from flask import render_template, request, session, redirect
from werkzeug.security import generate_password_hash
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time, uuid

# other python files
import x

from app import app

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
            
            return f"""<browser mix-redirect="/"></browser>"""

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

                    return f"""<browser mix-redirect="/"></browser>"""

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