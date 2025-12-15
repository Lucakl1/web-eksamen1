from flask import render_template, request
from werkzeug.security import generate_password_hash
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time

# other python files
import x

from app import app

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