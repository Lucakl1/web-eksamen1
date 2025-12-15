from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/unban")
def api_unban():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
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