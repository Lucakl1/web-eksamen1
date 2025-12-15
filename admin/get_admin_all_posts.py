from flask import render_template, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/get_admin_all_posts")
def get_admin_all_posts():
    try:
        # Validate user is admin
        ################
        user = session.get("user")
        if not user: return redirect(url_for('login'))

        if "admin" not in user['user_role']:
            return redirect("/")
        ################

        db, cursor = x.db()
        q = "SELECT COUNT(*) as total FROM posts"
        cursor.execute(q)
        all_posts_count = int(cursor.fetchone()["total"])
 
        q = "SELECT * FROM posts JOIN users ON user_fk = user_pk ORDER BY post_created_at DESC LIMIT 10"
        cursor.execute(q)
        all_posts = cursor.fetchall()


        template_fore_all_users = render_template("_____admin_all_posts.html", posts=all_posts, all_posts_count=all_posts_count)

        return f""" <browser mix-replace="#main">
            <main id="main" class="admin_all_posts"> 
                {template_fore_all_users}
            </main>
            </browser>
        """

    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()