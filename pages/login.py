from flask import render_template, request, session, redirect
from werkzeug.security import check_password_hash
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

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

            return f"""<browser mix-redirect="/"></browser>"""

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