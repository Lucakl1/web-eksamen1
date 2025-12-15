from flask import render_template, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/bookmark")
def view_bookmark():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        session["current_post_number"] = 0

        db, cursor = x.db()

        cursor.execute("SELECT COUNT(*) as total FROM posts JOIN bookmarks ON post_pk = post_fk WHERE post_deleted_at = 0 AND bookmarks.user_fk = %s", (user["user_pk"],))
        count = cursor.fetchone()["total"]
        session["max_number_of_posts"] = int(count)
        
        posts = x.get_posts(db, cursor, user, "bookmark", user["user_pk"])

        site = render_template("main_pages/bookmark.html", posts=posts, count=count)

        return f""" 
            <browser mix-replace='#main'> {site} </browser> 
            {x.page_title( x.lans('bookmarks'))} 
        """
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()