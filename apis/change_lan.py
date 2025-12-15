from flask import session, redirect, url_for
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/change_lan/<lan>")
def api_change_lan(lan = "english"):
    try:
        if lan not in x.allowed_languages: lan = "english"

        user = session.get("user")
        if not user: return redirect(url_for("login"))
        if lan in user['user_language']:
            return redirect("/")

        db, cursor = x.db()
        q = "UPDATE users SET user_language = %s WHERE user_pk = %s"
        cursor.execute(q, (lan, user['user_pk']))
        db.commit()

        session["user"]["user_language"] = lan

        return redirect("/")
    
    except Exception as ex:
        ic(ex)
        return {x.lans('system_under_maintenance')}, 400
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()