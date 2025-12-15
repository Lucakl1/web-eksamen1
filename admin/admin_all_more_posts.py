from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/admin_all_more_posts")
def admin_all_more_posts():
    try:
        # Validate user is admin
        ################
        user = session.get("user")
        if not user: return redirect(url_for('login'))

        if "admin" not in user['user_role']:
            return redirect("/")
        ################

        next_posts_count = int(request.args.get("current_count", ""))
        total_count = int(request.args.get("total_count", ""))
 
        db, cursor = x.db()
        q = "SELECT * FROM posts JOIN users ON user_fk = user_pk ORDER BY post_created_at DESC LIMIT 10 OFFSET %s"
        cursor.execute(q, (next_posts_count,))
        all_posts = cursor.fetchall()

        template_fore_all_posts = render_template("_____admin_more_posts.html", posts=all_posts)

        next_posts_count = next_posts_count + 10

        remove_more_button = f"""
            <browser mix-replace='#auto_show_more'>
                <button href="/admin_all_more_posts?total_count={total_count}&current_count={ next_posts_count }" mix-get mix-default="{ x.lans('more_posts') }" mix-await="{ x.lans('loading...') }" class="main_button" id="auto_show_more">
                    { x.lans('more_posts') }
                </button>
            </browser>"""
        
        if total_count <= next_posts_count: 
            remove_more_button = f"<browser mix-remove='#auto_show_more'></browser>"

        return f""" 
            <browser mix-bottom="#posts">{template_fore_all_posts}</browser>
            {remove_more_button}
        """

    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()