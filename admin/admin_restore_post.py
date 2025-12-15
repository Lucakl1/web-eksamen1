from flask import render_template, request
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.put("/admin_restore_post")
def api_admin_restore_post():
    try:
        post_pk = request.args.get("post", "")

        db, cursor = x.db()
        q = "UPDATE posts SET post_deleted_at = %s WHERE post_pk = %s" 
        cursor.execute(q, (0, post_pk))
        db.commit()

        new_button = f""" 
            <a href="/admin_delete_post?post={ post_pk }" mix-delete class="delete" id="admin_post_delete{ post_pk }"> { x.lans("remove_post") } </a>
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