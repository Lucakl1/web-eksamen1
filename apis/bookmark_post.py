from flask import render_template, request, session
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time

# other python files
import x

from app import app

@app.patch("/bookmark_post")
def api_bookmark_post():
    try:
        user_pk = session.get("user", "")["user_pk"]
        post_pk = int(request.args.get("post"))
        current_time = int(time.time())

        db, cursor = x.db()

        q = "SELECT * FROM bookmarks WHERE user_fk = %s AND post_fk = %s"
        cursor.execute(q, (user_pk, post_pk))
        existing_bookmark = cursor.fetchone()

        if existing_bookmark:
            q = "DELETE FROM bookmarks WHERE user_fk = %s AND post_fk = %s"
            existing_bookmark = False
            cursor.execute(q, (user_pk, post_pk))
        else:
            q = "INSERT INTO bookmarks VALUES(%s, %s, %s)"
            existing_bookmark = True
            cursor.execute(q, (user_pk, post_pk, current_time))

        db.commit()

        q = "SELECT post_total_bookmark FROM posts WHERE post_pk = %s"
        cursor.execute(q, (post_pk,))
        post_info = cursor.fetchone()

        post = {"post_total_bookmark": post_info["post_total_bookmark"], "post_pk": post_pk, "user_has_bookmarked": existing_bookmark}
        bookmark_template = render_template("___post_bookmark.html", post=post)

        return f"""
            <browser mix-replace='#bookmark_post{post_pk}'>
                {bookmark_template}
            </browser>
        """
    
    except Exception as ex:
        ic(ex)
        error_msg = {x.lans('something_happened_and_your_bookmark_did_not_get_saved')}
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>""", 400
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close() 