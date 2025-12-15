from flask import render_template, request
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/more_comments")
def api_more_comments():
    try:
        post_pk = request.args.get("post", "")
        current_count = int(request.args.get("current_count", ""))
        
        db, cursor = x.db()
        q = "SELECT * FROM comments JOIN users ON user_fk = user_pk WHERE post_fk = %s ORDER BY comment_created_at DESC LIMIT 5 OFFSET %s"
        cursor.execute(q, (post_pk, current_count))
        comments = cursor.fetchall()

        current_count = current_count + 5
        cursor.execute("SELECT COUNT(*) as total FROM comments WHERE post_fk = %s", (post_pk,))
        total_amount_of_comments = int(cursor.fetchone()["total"])


        template_comments = render_template("___append_more_comments.html", comments=comments, post_pk=post_pk, current_count=current_count, total_amount_of_comments=total_amount_of_comments)

        return f"""
            <browser mix-replace="#more_comments_button{post_pk}">{template_comments}<browser>
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