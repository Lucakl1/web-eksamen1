from flask import render_template
from icecream import ic
import x
from app import app

@app.get("/explore")
def view_explore():
    try:
        site = render_template("main_pages/explore.html", currently_selectet='users')
        return f""" 
        <browser mix-replace='#main'> {site} </browser> 
        {x.page_title(x.lans("explore"))}
        """
    except Exception as ex:
        ic(ex)
        return x.lans('system_under_maintenance')
    finally:
        pass