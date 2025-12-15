from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time

# other python files
import x

from app import app

@app.delete("/delete_profile_confirm")
def api_delete_profile_confirm():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
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