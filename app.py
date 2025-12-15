from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import requests
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import csv, io, json, time, uuid, os

# other python files
import x
from x import no_cache

app = Flask(__name__)

def _____USER_____(): pass 
##############################
##############################
##############################

########### Set up ###########
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.context_processor
def global_variables():
    return dict (
        x = x,
        user = session.get("user", "")
    )

@app.get("/logout")
def logout():
    try:
        session.clear()
        return redirect(url_for("login"))
    except Exception as ex:
        ic(ex)
        error_template = render_template(("global/error_message.html"), message=x.lans("error_please_try_again"))
        return f"""<browser mix-bottom='#error_response'>{ error_template }</browser>"""

##############################
##############################
# @app.route("/test", methods=["GET","POST"])
# @app.route("/test/<test_name>", methods=["GET","POST"])
# def view_tests(test_name = "all"):
#     try:
#         if test_name == "all":
#             all_the_html = ""
#             templates_path = os.listdir(os.path.join(app.root_path, 'templates/test'))
#             for file in templates_path:
#                 all_the_html += render_template(f"test/{file}")
#             return all_the_html
#         return render_template(f"test/{test_name}.html")
#     except:
#         return "either no pages was found, or an error in the code"
    
# @app.post('/upload')
# def upload_file():
#     if 'file' not in request.files:
#         return 'No file part'
    
#     file = request.files['file']
    
#     if file.filename == '':
#         return 'No selected file'
    
#     # til senere sæt en path i x filen UPLOAD_ITEM_FOLDER = './images'
#     file.save(os.path.join("static/uploads", file.filename))
#     return redirect("/test")
##############################
##############################

@app.get("/")
@no_cache
def view_index():
    try:
        x.site_name = x.lans("home")
        session["current_post_number"] = 0
        user = session.get("user")
        if not user: return redirect(url_for("login"))
        user_pk = user["user_pk"]

        lan = x.default_language = user["user_language"]
        if lan not in x.allowed_languages: lan = "english"
        x.default_language = lan

        db, cursor = x.db()

        cursor.execute("SELECT COUNT(*) FROM posts WHERE post_deleted_at = 0")
        count = cursor.fetchone()["COUNT(*)"]
        session["max_number_of_posts"] = int(count)     
        
        posts = x.get_posts(db, cursor, user)

        q = """SELECT 
        user_pk, user_username, user_avatar, user_first_name, user_last_name, user_username 
        FROM users 
        LEFT JOIN followers ON users.user_pk = followers.user_follows_fk 
        WHERE users.user_pk != %s 
        AND (followers.user_fk IS NULL OR followers.user_fk != %s)
        AND user_deleted_at = 0
        ORDER BY RAND() LIMIT 5"""
        cursor.execute(q, (user_pk, user_pk))
        recommended_users = cursor.fetchall()

        for rec_user in recommended_users:
            q = "SELECT * FROM followers WHERE user_fk = %s AND user_follows_fk = %s"
            cursor.execute(q, (user_pk, rec_user["user_pk"]))
            current_user_is_following = cursor.fetchone()

            rec_user["current_user_is_following"] = current_user_is_following

        return render_template("index.html", posts=posts, recommended_users=recommended_users, count=count)
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

# Main Pages
import pages.home
import pages.explore
import pages.profile
import pages.followers
import pages.following
import pages.edit_profile
import pages.bookmark
import pages.notifications

# Main Pages || Login | signup flow
import pages.login
import pages.signup
import pages.forgot_password
import pages.reset_password

# API
import apis.delete_profile
import apis.delete_profile_confirm
import apis.change_lan

import apis.follow
import apis.like_post
import apis.bookmark_post

import apis.make_a_post
import apis.edit_post
import apis.delete_post

import apis.api_comments
import apis.edit_comment
import apis.delete_comment

import apis.more_comments
import apis.get_more_posts_home
import apis.get_more_posts_profile
import apis.get_more_posts_bookmarked
import apis.get_more_posts_notifications
import apis.get_more_posts_explore_users
import apis.get_more_posts_explore_posts

import apis.aside_user_search
import apis.change_search_for
import apis.make_a_search_request
import apis.verify_account

# Admin pages / API's
import admin.unban
import admin.get_data_from_sheet
import admin.get_admin_all_users
import admin.get_admin_all_posts
import admin.admin_all_more_users
import admin.admin_all_more_posts
import admin.admin_delete_post
import admin.admin_restore_post
