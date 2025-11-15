from flask import request, make_response, render_template
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import re, json, os


########### Set up ###########
google_spread_sheet_key = "1UYgE2jJ__HYl0N7lA5JR3sMH75hwhzhPPsSRRA-WNdg"
allowed_languages = ["english", "danish", "spanish"]
default_language = "english"
site_name = "Home"

##############################
 
def lans(key):
    with open("dictionary.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data[key][default_language]

##############################
def db():
    try:
        host = "lucaklaeoe.mysql.eu.pythonanywhere-services.com" if "PYTHONANYWHERE_DOMAIN" in os.environ else "mariadb"
        user = "lucaklaeoe" if "PYTHONANYWHERE_DOMAIN" in os.environ else "root"
        password = "MyPasswordForYou" if "PYTHONANYWHERE_DOMAIN" in os.environ else "eksamen312luca"
        database = "lucaklaeoe$default" if "PYTHONANYWHERE_DOMAIN" in os.environ else "x"

        db = mysql.connector.connect(
            host = host,
            user = user,  
            password = password,
            database = database
        )
        cursor = db.cursor(dictionary=True)
        return db, cursor
    except Exception as ex:
        ic(ex)
        raise Exception("x exception - Database under maintenance", 500)


##############################
def no_cache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view


##############################
REGEX_EMAIL = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
def validate_user_email(user_email = None):
    if not user_email: user_email = request.form.get("user_email", "").strip()
    if not re.match(REGEX_EMAIL, user_email): raise Exception(f"x exception - {lans('invalid_email')}", 400)
    return user_email

##############################
USER_USERNAME_MIN = 2
USER_USERNAME_MAX = 20
REGEX_USER_USERNAME = f"^.{{{USER_USERNAME_MIN},{USER_USERNAME_MAX}}}$"
def validate_user_username(user_username = None):
    if not user_username: user_username = request.form.get("user_username", "").strip()
    if len(user_username) < USER_USERNAME_MIN: raise Exception(f"x exception - {lans('username_to_short_must_be_above')} {USER_USERNAME_MIN}", 400)
    if len(user_username) > USER_USERNAME_MAX: raise Exception(f"x exception - {lans('username_to_long_must_be_below')} {USER_USERNAME_MAX}", 400)
    return user_username


##############################
USER_FIRST_NAME_MIN = 2
USER_FIRST_NAME_MAX = 20
REGEX_USER_FIRST_NAME = f"^.{{{USER_FIRST_NAME_MIN},{USER_FIRST_NAME_MAX}}}$"
def validate_user_first_name():
    user_first_name = request.form.get("user_first_name", "").strip()
    if len(user_first_name) < USER_FIRST_NAME_MIN: raise Exception(f"x exception - {lans('first_name_to_short_must_be_above')} {USER_FIRST_NAME_MIN}", 400)
    if len(user_first_name) > USER_FIRST_NAME_MAX: raise Exception(f"x exception - {lans('first_name_to_long_must_be_below')} {USER_FIRST_NAME_MAX}", 400)
    return user_first_name

##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
REGEX_USER_LAST_NAME = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"
def validate_user_last_name():
    user_last_name = request.form.get("user_last_name", "").strip()
    if len(user_last_name) < USER_LAST_NAME_MIN: raise Exception(f"x exception - {lans('last_name_to_short_must_be_above')} {USER_FIRST_NAME_MIN}", 400)
    if len(user_last_name) > USER_LAST_NAME_MAX: raise Exception(f"x exception - {lans('last_name_to_long_must_be_below')} {USER_FIRST_NAME_MAX}", 400)
    return user_last_name


##############################
USER_PASSWORD_MIN = 6
USER_PASSWORD_MAX = 50
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"
def validate_user_password():
    user_password = request.form.get("user_password", "").strip()
    if len(user_password) < USER_PASSWORD_MIN: raise Exception(f"x exception - {lans('password_to_short_must_be_above')} {USER_PASSWORD_MIN}", 400)
    if len(user_password) > USER_PASSWORD_MAX: raise Exception(f"x exception - {lans('password_to_long_must_be_below')} {USER_PASSWORD_MAX}", 400)
    return user_password


##############################
def validate_user_password_confirm():
    user_password_confirm = request.form.get("user_password_confirm", "").strip()
    user_password = request.form.get("user_password", "").strip()
    if user_password != user_password_confirm : raise Exception(f"x exception - {lans('confirm_passwords_dont_match')}", 400)
    return user_password_confirm

##############################
USER_USERNAME_EMAIL_MIN = 2
USER_USERNAME_EMAIL_MAX = 100
REGEX_USERNAME_EMAIL_MAX = f"^.{{{USER_USERNAME_EMAIL_MIN},{USER_USERNAME_EMAIL_MAX}}}$"

##############################
def send_email(to_email, subject, template):
    try:
        sender_email = "lucaklaeoeskole@gmail.com"
        password = "yjno suwt geqp wcey"
        
        # Create the email message
        message = MIMEMultipart()
        message["From"] = lans("x_clone_eksamens_project")
        message["To"] = to_email
        message["Subject"] = subject

        # Body of the email
        message.attach(MIMEText(template, "html"))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, message.as_string())
        ic("Email sent successfully!")

        return "email sent"
       
    except Exception as ex:
        ic(ex)
        raise Exception("Cannot send email", 500)
    
##############################
REGEX_UUID4_WITHOUT_DASHES = "^[0-9a-f]{8}[0-9a-f]{4}4[0-9a-f]{3}[89ab][0-9a-f]{3}[0-9a-f]{12}$"
def validate_uuid4_without_dashes():
    user_uuid4 = request.args.get("key", "")
    ic(user_uuid4)
    if not re.match(REGEX_UUID4_WITHOUT_DASHES, user_uuid4): raise Exception(f"x exception - {lans('cannot_verify_user')}", 400) # TO ASK is this the right way to tell the user it wasn't a uuid
    return user_uuid4

##### need adjustment down from here ###############
##############################
REGEX_UUID4 = "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
def validate_uuid4(uuid4 = ""):
    if not uuid4:
        uuid4 = request.values.get("uuid4", "").strip()
    if not re.match(REGEX_UUID4, uuid4): raise Exception("Twitter exception - Invalid uuid4", 400)
    return uuid4

##############################
POST_MIN_LEN = 2
POST_MAX_LEN = 250
REGEX_POST = f"^.{{{POST_MIN_LEN},{POST_MAX_LEN}}}$"
def validate_post(post = ""):
    post = post.strip()
    if not re.match(REGEX_POST, post): raise Exception("x-error post", 400)
    return post