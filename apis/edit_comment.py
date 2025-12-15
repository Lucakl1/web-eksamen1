from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time

# other python files
import x

from app import app

@app.route("/edit_comment", methods=["GET", "POST"])
def api_edit_comment():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        comment_pk = request.args.get("comment", "")
        if comment_pk == "": raise Exception(f"x exception - {x.lans('comment_is_deleted')}", 400)
        db, cursor = x.db()

        q = "SELECT * FROM comments JOIN users ON user_pk = user_fk WHERE comment_pk = %s"
        cursor.execute(q, (comment_pk,))
        comment = cursor.fetchone()
        db.commit()

        if comment["user_fk"] != user["user_pk"]:
            raise Exception(f"x exception - {x.lans('you_dont_have_the_authority_to_edit_this_comment')}", 400)
        
        if request.method == "GET":
                
            edit_comment_template = render_template(("_edit_comment.html"), comment=comment)
            return f"""
                <browser mix-replace='#comment{comment_pk}'>{edit_comment_template}</browser>
            """
        
        if request.method == "POST":
            comment_message = x.validate_comment_message()
            current_time = int(time.time())


            q = "UPDATE comments SET comment_message = %s, comment_updated_at = %s WHERE comment_pk = %s"
            cursor.execute(q, (comment_message, current_time, comment_pk))

            comment = {}
            comment["comment_pk"] = comment_pk
            comment["user_fk"] = user["user_pk"]
            comment["comment_message"] = comment_message
            comment["comment_updated_at"] = current_time
            comment["comment_created_at"] = 0

            comment["user_username"] = user["user_username"]
            comment["user_banner"] = user["user_banner"]
            comment["user_avatar"] = user["user_avatar"]
            comment["user_first_name"] = user["user_first_name"]
            comment["user_last_name"] = user["user_last_name"]
            comment["user_created_at"] = user["user_created_at"]
            comment["user_bio"] = user["user_bio"]
            
            comment_template = render_template("_comment.html", comment=comment)
            succes_template = render_template(("global/succes_message.html"), message=x.lans("succes"))

            return f""" 
                <browser mix-replace="#comment{comment_pk}"> {comment_template} </browser> 
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