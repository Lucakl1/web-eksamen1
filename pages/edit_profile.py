from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time, os

# other python files
import x

from app import app

@app.route("/edit_profile", methods=["GET", "POST"])
def view_edit_profile():
    try:
        if request.method == "GET": 
            user_username = session.get("user", "")["user_username"]
            site = render_template("main_pages/edit_profile.html")
            return f""" 
                <browser mix-replace='#main'> {site} </browser>
                {x.page_title( x.lans('edit_profile') + " - " + user_username )} 
            """
        
        if request.method == "POST":
            user = session.get("user")
            if not user: return redirect(url_for("login"))
            user_avatar = x.validate_user_avatar()
            user_banner = x.validate_user_banner()
            user_username = x.validate_user_username()
            user_first_name = x.validate_user_first_name()
            user_last_name = x.validate_user_last_name()
            user_bio = x.validate_user_bio()
            current_time = int(time.time())

            db, cursor = x.db()
            
            if user_avatar != "":
                user_avatar.save(os.path.join(x.upload_user_folder_path, user_avatar.filename))
                user_avatar = user_avatar.filename

                q = "SELECT user_avatar FROM users WHERE user_pk = %s"
                cursor.execute(q, (user["user_pk"],))
                user_avatar_url = cursor.fetchone()["user_avatar"]

                old_path = os.path.join(x.upload_user_folder_path, user_avatar_url)
                if os.path.exists(old_path):
                    os.remove(old_path)
            else:
                user_avatar = user['user_avatar']

            if user_banner != "":
                user_banner.save(os.path.join(x.upload_user_folder_path, user_banner.filename))
                user_banner = user_banner.filename

                q = "SELECT user_banner FROM users WHERE user_pk = %s"
                cursor.execute(q, (user["user_pk"],))
                user_banner_url = cursor.fetchone()["user_banner"]
                
                old_path = os.path.join(x.upload_user_folder_path, user_banner_url)
                if os.path.exists(old_path):
                    os.remove(old_path)
            else:
                user_banner = user['user_banner']

            q = "UPDATE users SET user_avatar = %s, user_banner = %s, user_username = %s, user_first_name = %s, user_last_name = %s, user_bio = %s, user_updated_at = %s WHERE user_pk = %s"
            cursor.execute(q, (user_avatar, user_banner, user_username, user_first_name, user_last_name, user_bio, current_time, user['user_pk']))
            db.commit()

            session["user"]["user_avatar"] = user_avatar
            session["user"]["user_banner"] = user_banner
            session["user"]["user_username"] = user_username
            session["user"]["user_first_name"] = user_first_name
            session["user"]["user_last_name"] = user_last_name
            session["user"]["user_bio"] = user_bio


            succes_template = render_template(("global/succes_message.html"), message=x.lans("succes"))
            profile_tag = render_template(("___profile_tag.html"))

            cursor.execute("SELECT COUNT(*) as total FROM posts JOIN users ON user_pk = user_fk WHERE post_deleted_at = 0 AND user_username = %s", (user_username,))
            count = cursor.fetchone()["total"]
            session["max_number_of_posts"] = int(count)

            html_content_profile = render_template(("main_pages/profile.html"), userprofile=user, count=count)
            return f"""
                <browser mix-bottom='#succes_message'>{succes_template}</browser>
                <browser mix-replace='#profile_tag'>{profile_tag}</browser>
                <browser mix-replace='#main'>{html_content_profile}</browser>
            """

    except Exception as ex:
        ic(ex)
        error_code = str(ex)
        error_msg = x.lans('system_under_maintenance')
        if "x exception - " in error_code:
            error_msg = error_code.split("x exception - ")[1].split("',")[0].split('",')[0]

        if "Duplicate entry" in error_code:
            error_msg = x.lans("username_allready_in_system")
        
        error_template = render_template(("global/error_message.html"), message=error_msg)
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()