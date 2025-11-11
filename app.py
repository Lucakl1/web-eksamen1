from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import x 
import time
import uuid
import os

from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

app = Flask(__name__)

# Set the maximum file size to 10 MB
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024   # 1 MB

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
 

##############################
##############################
##############################
def _____USER_____(): pass 
##############################
##############################
##############################

@app.get("/")
def view_index():
    return render_template("index.html")


##############################
@app.get("/signup")
def view_signup():
    return render_template("signup.html")

##############################
@app.get("/login")
def view_login():
    return render_template("login.html")

##############################
@app.post("/login")
def handle_login():
    try:
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()
        db, cursor = x.db()
        q = "SELECT * FROM users WHERE user_email = %s and user_password = %s"
        cursor.execute(q, (user_email, user_password))
        user = cursor.fetchone()
        if not user: raise Exception("user not found", 400)
        session["user"] = user
        return redirect(url_for("view_home"))
    except Exception as ex:
        ic(ex)
        if ex.args[1] == 400: return ex.args[0]
        return "System under maintenance", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.get("/home")
@x.no_cache
def view_home():
    try:
        next_page = 1
    # user = session.get("user", "")
    # if not user: return redirect(url_for("view_login"))
        db, cursor = x.db()
        q = "SELECT * FROM users JOIN posts ON USER_PK = POST_USER_FK LIMIT 2"
        cursor.execute(q)
        tweets = cursor.fetchall()
        ic(tweets)

        q2 = "SELECT * FROM trends ORDER BY RAND() LIMIT 1"
        cursor.execute(q2)
        trends = cursor.fetchall()
        ic(trends)

        q3 = "SELECT * FROM users ORDER BY RAND() LIMIT 3"
        cursor.execute(q3)
        users_rows = cursor.fetchall()
        ic(users_rows)

        return render_template("home.html", tweets=tweets, trends=trends, users_rows=users_rows, next_page=next_page)
    except Exception as ex:
        ic(ex)
        return "error"
    finally:
        if "corsur" in locals(): cursor.close()
        if "db" in locals(): db.close()
        
@app.get ("/api-get-tweets")
def api_get_tweets():
    try:
        next_page = int(request.args.get("page", ""))
        # ic(next_page)
        db, cursor = x.db()
        q = "SELECT * FROM users JOIN posts ON user_pk = post_user_fk LIMIT %s,3"
        cursor.execute(q, (next_page*2,))
        tweets = cursor.fetchall()
        ic(tweets)
        
        container = ""
        for tweet in tweets[:2]:
            html_items = render_template("_tweet.html", tweet=tweet)
            container = container + html_items
        # ic(container)

        if(len(tweets) == 3):
            new_hyperlink = render_template("___show_more_tweets.html", next_page=next_page+1)
        else:
            new_hyperlink = ""

        return f"""
        <mixhtml mix-bottom="#tweets">
            {container}
        </mixhtml>
        <mixhtml mix-replace="#show_more">
            {new_hyperlink}
        </mixhtml>
        """
        # return render_template("items.html", items=items)
    except Exception as ex:
        ic(ex)
        return "error"
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()
        pass


##############################
@app.get("/logout")
def view_logout():
    session.clear()
    return redirect(url_for("view_login"))

##############################
@app.post("/signup")
def handle_signup():
    try:
        # Validate user name
        user_name = request.form.get("user_name", "").strip()
        x.validate_user_name(user_name)
        user_first_name = request.form.get("user_first_name", "").strip()
        x.validate_user_first_name(user_first_name)
        user_email = x.validate_user_email()
        db, cursor = x.db()
        db.start_transaction()
        q = "INSERT INTO users VALUES(null, %s, %s, %s)"
        cursor.execute(q, (user_name, user_first_name, user_email))
        inserted_rows = cursor.rowcount
        db.commit()
        return f"Total rows inserted: {inserted_rows}"
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()

        if "twitter exception - user name too short" in str(ex):
            return "name too short", 400

        if "twitter exception - user name too long" in str(ex):
            return "name too long", 400

        if "twitter exception - user first name too short" in str(ex):
            return "first name too short", 400

        if "twitter exception - user first name too long" in str(ex):
            return "first name too long", 400

        if "Twitter exception - Invalid email" in str(ex):
            return "Invalid email", 400

        if "Duplicate entry" and user_name in str(ex):
            return "username already registered", 400
        
        if "Duplicate entry" and user_email in str(ex):
            return "email already registered", 400   

        return "System under maintainance", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
@app.get ("/ajax")
def view_ajax ():
    try:
        return render_template("ajax.html")
    except Exception as ex:
        ic(ex)
    finally:
        pass

    ##############################
@app.get ("/tweet")
def api_tweet():
    try:
        return "You did it"
    except Exception as ex:
        ic(ex)
    finally:
        pass

##############################
@app.get ("/ajax_post")
def view_ajax_post():
    try:
        return render_template("ajax_post.html")
    except Exception as ex:
        ic(ex)
    finally:
        pass


##############################
@app.post ("/save")
def api_save ():
    try:
        user_name = request.form.get("user_name", "")
        user_last_name = request.form.get("user_last_name", "")
        user_nick_name = request.form.get("user_nick_name", "")

        # dictionary in Python is JSON in javascript 
        user = {
            "user_name" : user_name.upper(),
            "user_last_name" : user_last_name.title(),
            "user_nick_name" : user_nick_name.title(),
        }

        return user
    except Exception as ex:
        ic(ex)
    finally:
        pass

##############################
@app.get ("/ajax_heart")
def view_ajax_heart ():
    try:
        return render_template("ajax_heart.html")
    except Exception as ex:
        ic(ex)
    finally:
        pass


##############################
@app.get ("/api-like-tweet")
def api_like_tweet ():
    try:
        # TODO: Validate the data
        # TODO: Get the user logged user id
        # TODO: Connect to the database
        # TODO: Disconnect to the database
        # TODO: Insert the liking of a tweet in the table 
        # TODO: Check that everthing want fine as expected
        # TODO: Reply to the browser information that the tweet is liked 

        return {"status" : "ok"}
    except Exception as ex:
        ic(ex)
        return {"status" : "error"}
    finally:
        pass

##############################
@app.get ("/api-unlike-tweet")
def api_unlike_tweet ():
    try:
        # TODO: Validate the data
        # TODO: Get the user logged user id
        # TODO: Connect to the database
        # TODO: Disconnect to the database
        # TODO: Delete the liking of a tweet in the table 
        # TODO: Check that everthing want fine as expected
        # TODO: Reply to the browser information that the tweet is liked 

        return {"status" : "ok"}
    except Exception as ex:
        ic(ex)
        return {"status" : "error"}
    finally:
        pass

##############################
@app.get ("/ajax_bookmark")
def view_ajax_bookmark():
    try:
        return render_template("ajax_bookmark.html")
    except Exception as ex:
        ic(ex)
    finally:
        pass

##############################
@app.post ("/api-bookmark")
def api_bookmark():
    try:
        return """
        <mixhtml mix-replace='button'>
            <button mix-post="/api-remove-bookmark">
                <i class="fa-solid fa-bookmark"></i>
            </button>
        </mixhtml>
        <mixhtml mix-before='button'>
            <div mix-ttl="5000" mix-fade-out>I will disappear</div>
        </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        return "error"
    finally:
        pass


##############################
@app.get ("/items")
def view_items():
    try:
        next_page = 1
        db, cursor = x.db()
        q = "SELECT * FROM posts LIMIT 0,2"
        cursor.execute(q)
        items = cursor.fetchall()
        ic(items)
        return render_template("items.html", items=items, next_page=next_page)
    except Exception as ex:
        ic(ex)
        return "error"
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()
        pass

##############################
@app.get ("/api-get-items")
def api_get_items():
    try:
        next_page = int(request.args.get("page", ""))
        ic(next_page)
        db, cursor = x.db()
        q = "SELECT * FROM posts LIMIT %s,3"
        cursor.execute(q, (next_page*2,))
        items = cursor.fetchall()
        ic(items)
        
        container = ""
        for item in items[:2]:
            html_items = render_template("_item.html", item=item)
            container = container + html_items
        ic(container)

        if(len(items) == 3):
            new_hyperlink = render_template("___show_more.html", next_page=next_page+1)
        else:
            new_hyperlink = ""

        return f"""
        <mixhtml mix-bottom="#items">
            {container}
        </mixhtml>
        <mixhtml mix-replace="#show_more">
            {new_hyperlink}
        </mixhtml>
        """
        # return render_template("items.html", items=items)
    except Exception as ex:
        ic(ex)
        return "error"
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()
        pass

