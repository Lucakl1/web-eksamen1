from flask import render_template, request, session
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.patch("/like_post")
def api_like_post():
    try:
        user_pk = session.get("user", "")["user_pk"]
        post_pk = int(request.args.get("post"))

        db, cursor = x.db()

        q = "SELECT * FROM likes WHERE user_fk = %s AND post_fk = %s"
        cursor.execute(q, (user_pk, post_pk))
        existing_like = cursor.fetchone()

        if existing_like:
            q = "DELETE FROM likes WHERE user_fk = %s AND post_fk = %s"
            existing_like = False
        else:
            q = "INSERT INTO likes VALUES(%s, %s)"
            existing_like = True

        cursor.execute(q, (user_pk, post_pk))
        db.commit()

        q = "SELECT post_total_likes FROM posts WHERE post_pk = %s"
        cursor.execute(q, (post_pk,))
        post_info = cursor.fetchone()

        post = {"post_total_likes": post_info["post_total_likes"], "post_pk": post_pk, "user_has_liked": existing_like}
        like_template = render_template("___post_like.html", post=post)

        return f"""
            <browser mix-replace='#like_post{post_pk}'>
                {like_template}
            </browser>
        """
    
    except Exception as ex:
        ic(ex)
        error_msg = {x.lans('something_happend_and_like_did_not_get_saved')}
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>""", 400
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close() 