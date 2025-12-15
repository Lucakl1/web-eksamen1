from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time, os

# other python files
import x

from app import app

@app.route("/edit_post", methods=["GET", "POST"])
def api_edit_post():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        post_pk = request.args.get("post", "")
        if post_pk == "": raise Exception(f"x exception - {x.lans('post_is_deleted')}", 400)
        db, cursor = x.db()

        q = "SELECT * FROM posts JOIN users ON user_pk = user_fk WHERE post_pk = %s"
        cursor.execute(q, (post_pk,))
        post = cursor.fetchone()
        db.commit()

        if post["user_fk"] != user["user_pk"]:
            raise Exception(f"x exception - {x.lans('you_dont_have_the_authority_to_edit_this_post')}", 400)
        
        if request.method == "GET":
                
            edit_post_template = render_template(("_edit_post.html"), post=post)
            return f"""
                <browser mix-replace='#post{post_pk}'>{edit_post_template}</browser>
            """
        
        if request.method == "POST":
            current_time = int(time.time())
            new_post_message = x.validate_post_message()
            remove_media = request.form.get("delete_media", "")

            db.start_transaction()
            q = "UPDATE posts SET post_message = %s, post_updated_at = %s WHERE post_pk = %s"
            cursor.execute(q, (new_post_message, current_time, post_pk))

            category = ""
            if remove_media == "on":
                q = "DELETE FROM post_medias WHERE post_fk = %s"
                cursor.execute(q, (post_pk,))
            else:
                new_post_media = x.validate_post_media()
                
                if new_post_media != "":
                    ext = new_post_media.filename.rsplit(".", 1)[-1].lower()
                    new_post_media.save(os.path.join(x.upload_post_folder_path, new_post_media.filename))
                    new_post_media = new_post_media.filename

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

                    q = "SELECT * FROM post_medias WHERE post_fk = %s"
                    cursor.execute(q, (post_pk,))
                    media_allready_exists = cursor.fetchone()

                    if media_allready_exists:
                        q = "UPDATE post_medias SET post_media_path = %s, post_media_type_fk = %s WHERE post_fk = %s"
                        cursor.execute(q, (new_post_media, post_media_type_pk, post_pk))
                    else:
                        q = "INSERT INTO post_medias (post_fk, post_media_path, post_media_type_fk) VALUES (%s, %s, %s)"
                        cursor.execute(q, (post_pk, new_post_media, post_media_type_pk))
            db.commit()

            q = """
            SELECT 
            post_pk, post_created_at, post_deleted_at, post_message, post_pk, post_total_comments, post_total_likes, post_total_bookmark, post_updated_at,
            user_avatar, user_banner, user_bio, user_first_name, user_last_name, user_username, user_pk, user_created_at,
            post_media_type_fk, post_media_path
            FROM users 
            JOIN posts ON user_pk = user_fk
            LEFT JOIN post_medias ON post_pk = post_fk
            WHERE post_deleted_at = 0 AND post_pk = %s
            """
            cursor.execute(q, (post_pk,))
            post = cursor.fetchone()
            
            if category != "": post["post_media_type"] = category

            q = "SELECT * FROM likes WHERE user_fk = %s AND post_fk = %s"
            cursor.execute(q, (user["user_pk"], post_pk))
            existing_like = cursor.fetchone()
            
            q = "SELECT * FROM bookmarks WHERE user_fk = %s AND post_fk = %s"
            cursor.execute(q, (user["user_pk"], post_pk))
            existing_bookmark = cursor.fetchone()

            post["user_has_liked"] = existing_like
            post["user_has_bookmarked"] = existing_bookmark
            

            new_post = render_template("_post.html", post=post)
            succes_template = render_template(("global/succes_message.html"), message=x.lans("post_updated"))
            return f""" 
                <browser mix-replace="#post{post_pk}"> {new_post} </browser>
                <browser mix-bottom='#succes_message'>{succes_template}</browser>
            """

    except Exception as ex:
        if "db" in locals(): db.rollback()
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