from flask import render_template, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/profile")
@app.get("/profile/<user_username>")
def view_profile(user_username = ""):
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        
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