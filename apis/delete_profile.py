from flask import request
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/delete_profile")
def api_delete_profile():
    try:
        user_username = request.args.get("user", "")
        return f""" 
            <browser mix-replace="#delete_account">  
                <a class="secoundary_button red_button" mix-delete href="/delete_profile_confirm?user={user_username}">{ x.lans('are_you_sure_click_again') }</a>
            </browser>
        """
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')