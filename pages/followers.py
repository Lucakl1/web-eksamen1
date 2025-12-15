from flask import render_template, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/followers")
@app.get("/followers/<userprofile>")
def view_followers(userprofile = ""):
    try:
        if userprofile == "": userprofile = session.get("user")["user_username"]
        if userprofile == "": return redirect(url_for("login"))

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