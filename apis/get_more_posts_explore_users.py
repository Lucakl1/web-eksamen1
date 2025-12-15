from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/get_more_posts_explore_users")
def api_get_more_posts_explore_users():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        max_number_of_users = session.get("max_number_of_posts")
        current_user_number = session.get("current_post_number", 0) + 10
        session["current_post_number"] = current_user_number
        search_value = request.args.get("search_value", "")
        
        db, cursor = x.db()
        q = """SELECT 
            user_pk, user_username, user_avatar, user_first_name, user_last_name, user_username 
            FROM users 
            LEFT JOIN followers ON users.user_pk = followers.user_follows_fk 
            WHERE users.user_pk != %s
            AND (user_username LIKE %s OR user_first_name LIKE %s OR user_last_name LIKE %s)
            AND user_deleted_at = 0
            LIMIT 4
            OFFSET %s"""
        cursor.execute(q, (user["user_pk"], search_value, search_value, search_value, current_user_number))
        users = cursor.fetchall()

        remove_more_button = ""
        if max_number_of_users <= current_user_number + 10: 
            remove_more_button = f"<browser mix-remove='#auto_show_more'></browser>"

        htmlUsers = render_template("___recommended_users.html", recommended_users=users)

        return f""" 
            <browser mix-bottom="#users"> {htmlUsers} </browser>
            {remove_more_button}
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