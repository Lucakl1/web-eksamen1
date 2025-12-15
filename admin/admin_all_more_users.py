from flask import render_template, request, session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/admin_all_more_users")
def api_admin_all_users():
    try:
        # Validate user is admin
        ################
        user = session.get("user")
        if not user: return redirect(url_for('login'))

        if "admin" not in user['user_role']:
            return redirect("/")
        ################

        next_users_count = int(request.args.get("current_count", ""))
        total_count = int(request.args.get("total_count", ""))
 
        db, cursor = x.db()
        q = "SELECT * FROM users ORDER BY user_created_at ASC LIMIT 30 OFFSET %s"
        cursor.execute(q, (next_users_count,))
        all_users = cursor.fetchall()

        template_fore_all_users = render_template("_____admin_more_users.html", users=all_users)

        next_users_count = next_users_count + 30

        remove_more_button = f"""
            <browser mix-replace='#auto_show_more'>
                <button href="/admin_all_more_users?total_count={total_count}&current_count={ next_users_count }" mix-get mix-default="{ x.lans('more_users') }" mix-await="{ x.lans('loading...') }" class="main_button" id="auto_show_more">
                    { x.lans('more_users') }
                </button>
            </browser>"""
        
        if total_count <= next_users_count: 
            remove_more_button = f"<browser mix-remove='#auto_show_more'></browser>"

        return f""" 
            <browser mix-bottom="#users">{template_fore_all_users}</browser>
            {remove_more_button}
        """

    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()