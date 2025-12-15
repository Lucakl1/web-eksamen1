from flask import render_template, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/get_more_posts_notifications")
def api_get_more_posts_notifications():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        max_number_of_posts = session.get("max_number_of_posts")
        current_post_number = session.get("current_post_number", 0) + 5
        session["current_post_number"] = current_post_number

        db, cursor = x.db()
        posts = x.get_posts(db, cursor, user, "notifications", None, current_post_number)

        remove_more_button = ""
        if max_number_of_posts <= current_post_number + 5: 
            remove_more_button = f"<browser mix-remove='#auto_show_more'></browser>"

        htmlPosts = render_template("___append_more_posts.html", posts=posts)

        return f""" 
            <browser mix-bottom="#posts"> {htmlPosts} </browser>
            {remove_more_button}
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