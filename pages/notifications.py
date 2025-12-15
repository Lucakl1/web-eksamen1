from flask import render_template, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/notifications")
def view_notifications():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
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