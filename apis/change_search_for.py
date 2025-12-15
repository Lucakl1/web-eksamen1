from flask import render_template
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# other python files
import x

from app import app

@app.get("/change_search_for")
@app.get("/change_search_for/<search_fore>")
def api_change_search_for(search_fore = "users"):
    try:
        change_search_for = render_template("_change_search_for.html", currently_selectet=search_fore)
        return f"""<browser mix-replace="#search_selector"> {change_search_for} </browser>"""
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')