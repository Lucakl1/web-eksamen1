from flask import render_template, request
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import uuid

# other python files
import x

from app import app

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