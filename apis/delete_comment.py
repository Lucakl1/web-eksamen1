from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.delete("/delete_comment")
def api_delete_comment():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        comment_pk = request.args.get("comment", "")
        if comment_pk == "": raise Exception(f"x exception - {x.lans('comment_is_allready_deleted')}", 400)

        db, cursor = x.db()

        q = "SELECT * FROM comments WHERE comment_pk = %s"
        cursor.execute(q, (comment_pk,))
        comment = cursor.fetchone()

        if comment["user_fk"] != user["user_pk"]:
            if "admin" in user['user_role']:
                q = "SELECT * FROM posts JOIN users ON user_pk = user_fk WHERE comment_pk = %s"
                cursor.execute(q, (comment_pk,))
                comment = cursor.fetchone()

                x.default_language = comment["user_language"]
                message_to_user = render_template("___email_comment_deleted.html", comment=comment)
                x.send_email(comment["user_email"], x.lans("one_of_your_comment_has_been_deleted"), message_to_user)
                x.default_language = user["user_language"]
            else:
                raise Exception(f"x exception - {x.lans('you_dont_have_the_authority_to_delete_this_comment')}", 400)            
        
        q = "SELECT post_pk, post_total_comments FROM posts WHERE post_pk = (SELECT post_fk FROM comments WHERE comment_pk = %s)"
        cursor.execute(q, (comment_pk,))
        post = cursor.fetchone()

        q = "DELETE FROM comments WHERE comment_pk = %s"
        cursor.execute(q, (comment_pk,))
        db.commit()

        post["post_total_comments"] = post["post_total_comments"] - 1
            
        comment_count_template = render_template("___post_comment.html", post=post)
        succes_template = render_template(("global/succes_message.html"), message=x.lans("comment_deleted"))
        
        return f"""
            <browser mix-bottom='#succes_message'>{succes_template}</browser>
            <browser mix-remove='#comment{comment_pk}'></browser>
            <browser mix-replace="#comment_count{post["post_pk"]}">{comment_count_template}</browser>
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