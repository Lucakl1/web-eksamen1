from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time

# other python files
import x

from app import app

@app.get("/follow")
def api_follow():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
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