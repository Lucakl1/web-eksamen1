from flask import render_template, session, redirect, url_for
from icecream import ic
import x
from app import app

@app.get("/home")
def view_home():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        session["current_post_number"] = 0

        db, cursor = x.db()

        cursor.execute("SELECT COUNT(*) FROM posts WHERE post_deleted_at = 0")
        count = cursor.fetchone()["COUNT(*)"]
        session["max_number_of_posts"] = int(count) 

        posts = x.get_posts(db, cursor, user)
        
        site = render_template("main_pages/home.html", posts=posts, count=count)
        return f""" 
        <browser mix-replace='#main'> {site} </browser> 
        {x.page_title(x.lans("home"))}
        """
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()