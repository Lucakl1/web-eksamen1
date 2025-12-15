from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.post("/make_a_search_request")
def api_make_a_search_request():
    try:
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        user_pk = user["user_pk"]
        search_value = request.form.get('search_for_value', '')
        search_for = request.form.get('search_for', '')

        db, cursor = x.db()
        if search_for == "users":
            search_value = f"{search_value}%"
            cursor.execute("""SELECT COUNT(*) as total FROM users 
                WHERE users.user_pk != %s AND (user_username LIKE %s OR user_first_name LIKE %s OR user_last_name LIKE %s) 
                AND user_deleted_at = 0""", 
                (user_pk, search_value, search_value, search_value))        
            count = int(cursor.fetchone()["total"])
            session["max_number_of_posts"] = int(count)

            q = """SELECT 
            user_pk, user_username, user_avatar, user_first_name, user_last_name, user_username 
            FROM users 
            LEFT JOIN followers ON users.user_pk = followers.user_follows_fk 
            WHERE users.user_pk != %s
            AND (user_username LIKE %s OR user_first_name LIKE %s OR user_last_name LIKE %s)
            AND user_deleted_at = 0
            LIMIT 10"""
            cursor.execute(q, (user_pk, search_value, search_value, search_value))
            users = cursor.fetchall()

            for result_user in users:
                q = "SELECT * FROM followers WHERE user_fk = %s AND user_follows_fk = %s"
                cursor.execute(q, (user_pk, result_user["user_pk"]))
                current_user_is_following = cursor.fetchone()

                result_user["current_user_is_following"] = current_user_is_following

            search_results_template = render_template("___search_users_result.html", users=users, count=count, search_value=search_value)
        
        elif search_for == "posts":

            cursor.execute("""SELECT COUNT(*) as total FROM users JOIN posts ON user_pk = user_fk WHERE post_deleted_at = 0 AND user_deleted_at = 0 AND MATCH(post_message) AGAINST("%s" IN NATURAL LANGUAGE MODE WITH QUERY EXPANSION)""", (search_value,))        
            count = int(cursor.fetchone()["total"])
            posts = x.get_posts(db, cursor, user, "explore", search_value)
            session["max_number_of_posts"] = int(count)
            
            search_results_template = render_template("___search_posts_result.html", posts=posts, count=count, search_value=search_value)

        return f"""<browser mix-replace="#search_content"> 
            <section id="search_content">
                {search_results_template} 
            </section>
        </browser>"""
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()