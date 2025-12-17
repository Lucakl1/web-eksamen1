from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.put("/restore_post")
def api_restore_post():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        post_pk = request.args.get("post", "")
        if post_pk == "": raise Exception(f"x exception - {x.lans('post_is_allready_deleted')}", 400)

        db, cursor = x.db()

        q = "SELECT * FROM posts WHERE post_pk = %s"
        cursor.execute(q, (post_pk,))
        post = cursor.fetchone()

        if post["user_fk"] != user["user_pk"]:
            if "admin" in user['user_role']:
                q = "SELECT user_first_name, user_last_name, user_language, post_message, user_email FROM posts JOIN users ON user_pk = user_fk WHERE post_pk = %s"
                cursor.execute(q, (post_pk,))
                post = cursor.fetchone()

                x.default_language = post["user_language"]
                message_to_user = render_template("___email_post_restore.html", post=post)
                x.send_email(post["user_email"], x.lans("one_of_your_post_has_been_restore"), message_to_user)
                x.default_language = user["user_language"]
            else:
                raise Exception(f"x exception - {x.lans('you_dont_have_the_authority_to_restore_this_post')}", 400)            
        
        q = "UPDATE posts SET post_deleted_at = 0 WHERE post_pk = %s"
        cursor.execute(q, (post_pk, ))
        db.commit()
            
        succes_template = render_template(("global/succes_message.html"), message=x.lans("post_restored"))
        return f"""
            <browser mix-bottom='#succes_message'>{succes_template}</browser>
            <browser mix-remove='#post{post_pk}'></browser>
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