from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time

# other python files
import x

from app import app

@app.route("/comments", methods=["GET", "POST"])
def api_comments():
    try:
        post_pk = request.args.get("post", "")
        db, cursor = x.db()

        if request.method == "GET":
            q = "SELECT * FROM comments JOIN users ON user_fk = user_pk WHERE post_fk = %s ORDER BY comment_created_at DESC LIMIT 5"
            cursor.execute(q, (post_pk,))
            comments = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) as total FROM comments WHERE post_fk = %s", (post_pk,))
            count = int(cursor.fetchone()["total"])

            template_comments = render_template("_append_comments.html", comments=comments, post_pk=post_pk, count=count)

            return f"""<browser mix-replace="#comments{post_pk}"> {template_comments} </browser>"""
        
        if request.method == "POST":
            user = session.get("user")
            if not user: return redirect(url_for("login"))
            user_pk = user["user_pk"]
            comment_message = x.validate_comment_message()
            current_time = int(time.time())

            q = "INSERT INTO comments (post_fk, user_fk, comment_message, comment_created_at) VALUES(%s, %s, %s, %s)"
            cursor.execute(q, (post_pk, user_pk, comment_message, current_time))
            db.commit()
            comment_pk = cursor.lastrowid

            q = "SELECT post_pk, post_total_comments FROM posts WHERE post_pk = %s"
            cursor.execute(q, (post_pk,))
            post = cursor.fetchone()

            comment = {}
            comment["comment_pk"] = comment_pk
            comment["post_fk"] = post_pk
            comment["user_fk"] = user_pk
            comment["comment_message"] = comment_message
            comment["comment_created_at"] = current_time
            comment["comment_updated_at"] = 0

            comment["user_username"] = user["user_username"]
            comment["user_banner"] = user["user_banner"]
            comment["user_avatar"] = user["user_avatar"]
            comment["user_first_name"] = user["user_first_name"]
            comment["user_last_name"] = user["user_last_name"]
            comment["user_created_at"] = user["user_created_at"]
            comment["user_bio"] = user["user_bio"]
            
            comment_template = render_template("_comment.html", comment=comment)
            comment_count_template = render_template("___post_comment.html", post=post)
            succes_template = render_template(("global/succes_message.html"), message=x.lans("succes"))
            post_comment_form = render_template(("___post_comment_form.html"), post_pk=post_pk)

            return f""" 
                <browser mix-top="#all_comments{post_pk}">{comment_template}</browser> 
                <browser mix-replace="#comment_count{post_pk}">{comment_count_template}</browser>
                <browser mix-bottom='#succes_message'>{succes_template}</browser>
                <browser mix-replace='#comments_form{post_pk}'>{post_comment_form}</browser>
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