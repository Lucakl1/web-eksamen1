from flask import render_template, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time, os

# other python files
import x

from app import app

@app.post("/make_a_post")
def api_make_a_post():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        post_message = x.validate_post_message()
        post_media = x.validate_post_media()
        current_time = int(time.time())

        db, cursor = x.db()
        db.start_transaction()
        q = "INSERT INTO posts (user_fk, post_message, post_created_at) VALUES (%s, %s, %s)"
        cursor.execute(q, (user['user_pk'], post_message, current_time))
        post_pk = cursor.lastrowid

        if post_media != "":
            ext = post_media.filename.rsplit(".", 1)[-1].lower()
            post_media.save(os.path.join(x.upload_post_folder_path, post_media.filename))
            post_media = post_media.filename

            if ext in {"jpg", "jpeg", "png", "webp"}:
                category = "image"
            elif ext in {"mp4"}:
                category = "video"
            elif ext in {"mp3"}:
                category = "audio"
            elif ext in {"pdf", "txt"}:
                category = "file"

            q = "SELECT post_media_type_pk FROM post_media_types WHERE post_media_type_type = %s"
            cursor.execute(q, (category,))
            post_media_type_pk = cursor.fetchone()["post_media_type_pk"]

            q = "INSERT INTO post_medias (post_fk, post_media_path, post_media_type_fk) VALUES (%s, %s, %s)"
            cursor.execute(q, (post_pk, post_media, post_media_type_pk))

        db.commit()

        if post_media != "":
            q = "SELECT * FROM posts JOIN post_medias ON post_pk = post_fk WHERE post_pk = %s"
            cursor.execute(q, (post_pk,))
            post = cursor.fetchone()

            q = "SELECT post_media_type_type FROM post_media_types WHERE post_media_type_pk = %s"
            cursor.execute(q, (post["post_media_type_fk"],))
            post_media_type = cursor.fetchone()
        else:
            q = "SELECT * FROM posts WHERE post_pk = %s"
            cursor.execute(q, (post_pk,))
            post = cursor.fetchone()

        post["user_username"] = user["user_username"]
        post["user_banner"] = user["user_banner"]
        post["user_avatar"] = user["user_avatar"]
        post["user_first_name"] = user["user_first_name"]
        post["user_last_name"] = user["user_last_name"]
        post["user_created_at"] = user["user_created_at"]
        post["user_bio"] = user["user_bio"]
        post["user_pk"] = user["user_pk"]
        if post_media != "": post["post_media_type"] = post_media_type["post_media_type_type"]

        html_content_post = render_template("_post.html", post=post)
        html_content_home_post_form = render_template("___home_post_form.html", post=post)
        succes_template = render_template(("global/succes_message.html"), message=x.lans("succes"))
        
        return f"""
            <browser mix-top='#posts'>{html_content_post}</browser>
            <browser mix-replace='#make_a_post'>{html_content_home_post_form}</browser>
            <browser mix-bottom='#succes_message'>{succes_template}</browser>
        """
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close() 