from flask import render_template, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/get_admin_all_users")
def get_admin_all_users():
    try:
        # Validate user is admin
        ################
        user = session.get("user")
        if not user: return redirect(url_for('login'))

        if "admin" not in user['user_role']:
            return redirect("/")
        ################

        db, cursor = x.db()
        q = "SELECT COUNT(*) as total FROM users"
        cursor.execute(q)
        all_user_count = int(cursor.fetchone()["total"])
 
        q = "SELECT * FROM users ORDER BY user_created_at ASC LIMIT 30"
        cursor.execute(q)
        all_users = cursor.fetchall()

        template_fore_all_users = render_template("_____admin_all_users.html", users=all_users, all_user_count=all_user_count)

        return f""" <browser mix-replace="#main">
            <main id="main" class="admin_all_users"> 
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