from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.post("/aside_user_search")
def api_aside_user_search():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        user_pk = user["user_pk"]
        user_search = f"{request.form.get('user_name_search', '')}%"

        recommended_users = ""
        if user_search != "%":
            db, cursor = x.db()
            q = """SELECT 
            user_pk, user_username, user_avatar, user_first_name, user_last_name, user_username 
            FROM users 
            LEFT JOIN followers ON users.user_pk = followers.user_follows_fk 
            WHERE users.user_pk != %s
            AND (user_username LIKE %s OR user_first_name LIKE %s OR user_last_name LIKE %s)
            AND user_deleted_at = 0
            LIMIT 7"""
            cursor.execute(q, (user_pk, user_search, user_search, user_search))
            recommended_users = cursor.fetchall()

            for rec_user in recommended_users:
                q = "SELECT * FROM followers WHERE user_fk = %s AND user_follows_fk = %s"
                cursor.execute(q, (user_pk, rec_user["user_pk"]))
                current_user_is_following = cursor.fetchone()

                rec_user["current_user_is_following"] = current_user_is_following

        recommended_users_template = f"<div id='search_results' class='recommended_users'> {render_template('___recommended_users.html', recommended_users=recommended_users)} </div>"

        return f"""<browser mix-replace="#search_results"> {recommended_users_template} </browser>"""
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()