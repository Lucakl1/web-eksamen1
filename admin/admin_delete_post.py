from flask import render_template, request
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time

# other python files
import x

from app import app

@app.delete("/admin_delete_post")
def api_admin_delete_post():
    try:
        post_pk = request.args.get("post", "")
        current_time = int(time.time())

        db, cursor = x.db()
        q = "UPDATE posts SET post_deleted_at = %s WHERE post_pk = %s" 
        cursor.execute(q, (current_time, post_pk))
        db.commit()

        new_button = f""" 
            <a href="/admin_restore_post?post={ post_pk }" mix-put class="delete" id="admin_post_delete{ post_pk }"> { x.lans("restore_post") } </a>
        """
        succes_template = render_template(("global/succes_message.html"), message=x.lans("succes"))
        return f"""
        <browser mix-replace='#admin_post_delete{post_pk}'> {new_button}</browser>
        <browser mix-bottom='#succes_message'>{succes_template}</browser>
        """
    except Exception as ex:
        ic(ex)
        error_template = render_template(("global/error_message.html"), message=x.lans("error_please_try_again"))
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()