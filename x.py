from flask import request, make_response
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
from datetime import datetime
import re, json, os, uuid


########### Set up ###########
google_spread_sheet_key = "1UYgE2jJ__HYl0N7lA5JR3sMH75hwhzhPPsSRRA-WNdg"
base_url = "https://lucaklaeoe.eu.pythonanywhere.com" if "PYTHONANYWHERE_DOMAIN" in os.environ else "http://127.0.0.1"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
upload_post_folder_path = os.path.join(BASE_DIR, "static", "posts_uploads")
upload_user_folder_path = os.path.join(BASE_DIR, "static", "users_uploads")
allowed_languages = ["english", "danish", "spanish"]
default_language = "english"
MAGIC_BYTES = {
    #images
    "png": b"\x89PNG\r\n\x1a\n",
    "jpg": {b"\xff\xd8\xff\xe0", b"\xff\xd8\xff\xe1", b"\xff\xd8\xff\xe8"},
    "webp": [b"RIFF", b"WEBP"],

    #text files
    "pdf": [b"%PDF"],

    #audio
    "mp3": {b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"},  

    #video
    "mp4": b"ftyp", 
    
    # Text
    "txt": None,
}

##############################
###### Helper functions ######
##############################
def lans(key):
    file_path = os.path.join(BASE_DIR, "dictionary.json")

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data[key][default_language]

##############################
def db():
    try:
        host = "lucaklaeoe.mysql.eu.pythonanywhere-services.com" if "PYTHONANYWHERE_DOMAIN" in os.environ else "mariadb"
        user = "lucaklaeoe" if "PYTHONANYWHERE_DOMAIN" in os.environ else "root"
        password = "MyPasswordForYou" if "PYTHONANYWHERE_DOMAIN" in os.environ else "eksamen312luca"
        database = "lucaklaeoe$x" if "PYTHONANYWHERE_DOMAIN" in os.environ else "x"

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

site_name = "Home"
def page_title(title = "Home"):
    return f""" <browser mix-replace="#title"> <title id="title">X - {title}</title> </browser> """

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
#### Validater functions #####
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
    if "@" in user_username: raise Exception(f"x exception - {lans('@_cant_be_in_username')}", 400)
    if " " in user_username: raise Exception(f"x exception - {lans('username_cant_have_spaces')}", 400)
    if len(user_username) < USER_USERNAME_MIN: raise Exception(f"x exception - {lans('username_to_short_must_be_above')} {USER_USERNAME_MIN}", 400)
    if len(user_username) > USER_USERNAME_MAX: raise Exception(f"x exception - {lans('username_to_long_must_be_below')} {USER_USERNAME_MAX}", 400)
    return user_username

##############################
USER_USERNAME_EMAIL_MIN = 2
USER_USERNAME_EMAIL_MAX = 100
REGEX_USERNAME_EMAIL_MAX = f"^.{{{USER_USERNAME_EMAIL_MIN},{USER_USERNAME_EMAIL_MAX}}}$"

##############################
USER_FIRST_NAME_MIN = 2
USER_FIRST_NAME_MAX = 20
REGEX_USER_FIRST_NAME = f"^.{{{USER_FIRST_NAME_MIN},{USER_FIRST_NAME_MAX}}}$"
def validate_user_first_name():
    user_first_name = request.form.get("user_first_name", "").strip()
    if "@" in user_first_name : raise Exception(f"x exception - {lans('@_cant_be_in_first_name')}", 400)
    if " " in user_first_name: raise Exception(f"x exception - {lans('first_name_cant_have_spaces')}", 400)
    if len(user_first_name) < USER_FIRST_NAME_MIN: raise Exception(f"x exception - {lans('first_name_to_short_must_be_above')} {USER_FIRST_NAME_MIN}", 400)
    if len(user_first_name) > USER_FIRST_NAME_MAX: raise Exception(f"x exception - {lans('first_name_to_long_must_be_below')} {USER_FIRST_NAME_MAX}", 400)
    return user_first_name

##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
REGEX_USER_LAST_NAME = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"
def validate_user_last_name():
    user_last_name = request.form.get("user_last_name", "").strip()
    if "@" in user_last_name : raise Exception(f"x exception - {lans('@_cant_be_in_first_name')}", 400)
    if " " in user_last_name: raise Exception(f"x exception - {lans('last_name_cant_have_spaces')}", 400)
    if len(user_last_name) < USER_LAST_NAME_MIN: raise Exception(f"x exception - {lans('last_name_to_short_must_be_above')} {USER_FIRST_NAME_MIN}", 400)
    if len(user_last_name) > USER_LAST_NAME_MAX: raise Exception(f"x exception - {lans('last_name_to_long_must_be_below')} {USER_FIRST_NAME_MAX}", 400)
    return user_last_name


##############################
USER_BIO_MIN = 1
USER_BIO_MAX = 200
REGEX_USER_BIO = f"^.{{{USER_BIO_MIN},{USER_BIO_MAX}}}$"
def validate_user_bio():
    user_bio = request.form.get("user_bio", "").strip()
    if len(user_bio) < USER_BIO_MIN: raise Exception(f"x exception - {lans('bio_to_short_must_be_above')} {USER_BIO_MIN}", 400)
    if len(user_bio) > USER_BIO_MAX: raise Exception(f"x exception - {lans('bio_to_long_must_be_below')} {USER_BIO_MAX}", 400)
    return user_bio

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
def validate_file(file, allowed_extenstions, allowed_mime_types, max_filesize_mb):
    if file.content_type == "application/octet-stream":
        raise Exception(f"x exception - {lans('file_is_not_recognized')}", 400)

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed_extenstions:
        raise Exception(f"x exception - {lans('file_extension')} .{ext} {lans('is_not_allowed')}", 400)

    file.filename = f"{uuid.uuid4().hex}.{ext}"
    if not file.filename:
        raise Exception("x exception - Invalid filename", 400)
    
    if file.mimetype not in allowed_mime_types:
        raise Exception(f"x exception - {lans('file_type')} '{file.mimetype}' {lans('is_not_allowed')}", 400)

    file.seek(0, 2)
    file_size = file.tell()
    # 1048576 = 1MB
    if file_size > max_filesize_mb * 1048576:
        raise Exception(f"x exception - {lans('file_exceeds_max_size_of')} {max_filesize_mb} MB", 400)
    file.seek(0)

    header = file.read(32)
    file.seek(0)

    if ext == "png":
        if not header.startswith(MAGIC_BYTES["png"]):
            raise Exception(f"x exception - {lans('file_content_does_not_match')} PNG {lans('format')}", 400)
    elif ext == "jpg":
        if not header.startswith(tuple(MAGIC_BYTES["jpg"])):
            raise Exception(f"x exception - {lans('file_content_does_not_match')} JPG {lans('format')}", 400)
    elif ext == "jpeg":
        if not header.startswith(tuple(MAGIC_BYTES["jpg"])):
            raise Exception(f"x exception - {lans('file_content_does_not_match')} JPEG {lans('format')}", 400)
    elif ext == "webp":
        if not (header[:4] == MAGIC_BYTES["webp"][0] and header[8:12] == MAGIC_BYTES["webp"][1]):
            raise Exception(f"x exception - {lans('file_content_does_not_match')} WebP {lans('format')}", 400)
    elif ext == "pdf":
        if not header.startswith(MAGIC_BYTES["pdf"][0]):
            raise Exception(f"x exception - {lans('file_content_does_not_match')} PDF {lans('format')}", 400)
    elif ext == "mp3":
        if not header.startswith(tuple(MAGIC_BYTES["mp3"])):
            raise Exception(f"x exception - {lans('file_content_does_not_match')} MP3 {lans('format')}", 400)
    elif ext == "mp4":
        if MAGIC_BYTES["mp4"] not in header:
            raise Exception(f"x exception - {lans('file_content_does_not_match')} MP4 {lans('format')}", 400)

    return file

ALLOWED_AVATAR_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
ALLOWED_AVATAR_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_AVATAR_FILESIZE_MB = 2

def validate_user_avatar():
    user_avatar = request.files.get("user_avatar", "")
    if not user_avatar or user_avatar.filename == "" or user_avatar.content_type == "application/octet-stream": return ""
    
    user_avatar = validate_file(user_avatar, ALLOWED_AVATAR_EXTENSIONS, ALLOWED_AVATAR_MIME_TYPES, MAX_AVATAR_FILESIZE_MB)

    return user_avatar

ALLOWED_BANNER_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
ALLOWED_BANNER_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_BANNER_FILESIZE_MB = 5
def validate_user_banner():
    user_banner = request.files.get("user_banner", "")
    if not user_banner or user_banner.filename == "" or user_banner.content_type == "application/octet-stream": return ""
    
    user_banner = validate_file(user_banner, ALLOWED_BANNER_EXTENSIONS, ALLOWED_BANNER_MIME_TYPES, MAX_BANNER_FILESIZE_MB)

    return user_banner

##############################
ALLOWED_POST_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "txt", "mp4", "pdf", "mp3"}
ALLOWED_POST_MIME_TYPES = {"image/png", "image/jpeg", "image/webp", "text/plain", "video/mp4", "application/pdf", "audio/mpeg"}
MAX_POST_FILESIZE_MB = 50
def validate_post_media():
    post_media = request.files.get("post_media", "")

    if not post_media or post_media.filename == "": return ""
    
    post_media = validate_file(post_media, ALLOWED_POST_EXTENSIONS, ALLOWED_POST_MIME_TYPES, MAX_POST_FILESIZE_MB)

    return post_media

##############################
POST_MESSAGE_MIN = 1
POST_MESSAGE_MAX = 200
REGEX_POST_MESSAGE = f"^.{{{POST_MESSAGE_MIN},{POST_MESSAGE_MAX}}}$"
def validate_post_message():
    post_message = request.form.get("post_message", "").strip()
    if len(post_message) < POST_MESSAGE_MIN: raise Exception(f"x exception - {lans('post_to_short_must_be_above')} {POST_MESSAGE_MIN}", 400)
    if len(post_message) > POST_MESSAGE_MAX: raise Exception(f"x exception - {lans('post_to_long_must_be_below')} {POST_MESSAGE_MAX}", 400)
    return post_message

##############################
COMMENT_MESSAGE_MIN = 1
COMMENT_MESSAGE_MAX = 100
REGEX_COMMENT_MESSAGE = f"^.{{{COMMENT_MESSAGE_MIN},{COMMENT_MESSAGE_MAX}}}$"
def validate_comment_message():
    comment_message = request.form.get("comment_message", "").strip()
    if len(comment_message) < COMMENT_MESSAGE_MIN: raise Exception(f"x exception - {lans('comment_to_short_must_be_above')} {COMMENT_MESSAGE_MIN}", 400)
    if len(comment_message) > COMMENT_MESSAGE_MAX: raise Exception(f"x exception - {lans('comment_to_long_must_be_below')} {COMMENT_MESSAGE_MAX}", 400)
    return comment_message
    
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
# db = database
# cursor = cursor
# user = current user (to see if user have likeed and more)
# witch_page (home page gets defrient posts then profile)
# data_fore_page (if the page needs any data)
# where_in_list (how long in the dfatabase have we scrolled)
def get_posts(db, cursor, user, witch_page = "home", data_fore_page = "", where_in_list = 0):

    q = """
        SELECT 
        post_pk, post_created_at, post_deleted_at, post_message, post_pk, post_total_comments, post_total_likes, post_total_bookmark, post_updated_at,
        user_avatar, user_banner, user_bio, user_first_name, user_last_name, user_username, user_pk, user_created_at,
        post_media_type_fk, post_media_path
        FROM users
        JOIN posts ON user_pk = user_fk"""
    if witch_page == "home":
        q = q + """
        LEFT JOIN post_medias ON post_pk = post_fk
        WHERE post_deleted_at = 0 AND user_deleted_at = 0
        ORDER BY post_created_at DESC LIMIT 5 OFFSET %s"""
        cursor.execute(q, (where_in_list,))
    elif witch_page == "profile":
        q = q + """
        LEFT JOIN post_medias ON post_pk = post_fk
        WHERE post_deleted_at = 0 AND user_deleted_at = 0 AND user_username = %s
        ORDER BY post_created_at DESC LIMIT 5 OFFSET %s"""
        cursor.execute(q, (data_fore_page, where_in_list))
    elif witch_page == "bookmark":
        q = q + """
        JOIN bookmarks ON post_pk = bookmarks.post_fk
        LEFT JOIN post_medias ON post_pk = post_medias.post_fk
        WHERE post_deleted_at = 0 AND user_deleted_at = 0 AND bookmarks.user_fk = %s
        ORDER BY post_created_at DESC LIMIT 5 OFFSET %s"""
        cursor.execute(q, (data_fore_page, where_in_list))
    elif witch_page == "notifications":
        q = q + """
        JOIN followers ON user_pk = user_follows_fk
        LEFT JOIN post_medias ON post_pk = post_medias.post_fk
        WHERE post_deleted_at = 0 AND user_deleted_at = 0
        ORDER BY post_created_at DESC LIMIT 5 OFFSET %s"""
        cursor.execute(q, (where_in_list,))
    elif witch_page == "explore":
        q = q + """
        LEFT JOIN post_medias ON post_pk = post_medias.post_fk
        WHERE post_deleted_at = 0 AND user_deleted_at = 0
        AND MATCH(post_message) AGAINST("%s" IN NATURAL LANGUAGE MODE WITH QUERY EXPANSION)
        ORDER BY post_created_at DESC LIMIT 5 OFFSET %s"""
        # not sure wether to user "IN NATURAL LANGUAGE MODE" or not
        # It seams to make the understanding wider therefore i am useing it
        # Same with "WITH QUERY EXPANSION"
        cursor.execute(q, (data_fore_page, where_in_list))

    posts = cursor.fetchall()

    for post in posts:
        # wether or not current user have liked
        user_pk = user['user_pk']
        post_pk = post['post_pk']

        q = "SELECT * FROM likes WHERE user_fk = %s AND post_fk = %s"
        cursor.execute(q, (user_pk, post_pk))
        existing_like = cursor.fetchone()

        post['user_has_liked'] = False
        if existing_like: post['user_has_liked'] = True
        
        q = "SELECT * FROM bookmarks WHERE user_fk = %s AND post_fk = %s"
        cursor.execute(q, (user_pk, post_pk))
        existing_bookmark = cursor.fetchone()

        post['user_has_bookmarked'] = False
        if existing_bookmark: post['user_has_bookmarked'] = True

        # what type of media
        if post["post_media_type_fk"]:
            q = "SELECT post_media_type_type FROM post_media_types WHERE post_media_type_pk = %s"
            cursor.execute(q, (post["post_media_type_fk"],))
            post_media_type = cursor.fetchone()["post_media_type_type"]

            if post_media_type: post['post_media_type'] = post_media_type
    
    return posts
    
##############################
REGEX_UUID4_WITHOUT_DASHES = "^[0-9a-f]{8}[0-9a-f]{4}4[0-9a-f]{3}[89ab][0-9a-f]{3}[0-9a-f]{12}$"
def validate_uuid4_without_dashes():
    user_uuid4 = request.args.get("key", "")
    ic(user_uuid4)
    if not re.match(REGEX_UUID4_WITHOUT_DASHES, user_uuid4): raise Exception(f"x exception - {lans('cannot_verify_user')}", 400)
    return user_uuid4

##############################
### Jinja helper functions ###
##############################
def time_ago(epoch_time):
    if epoch_time == 0:
        return ""
    
    current_time = datetime.now()
    datetimet = datetime.fromtimestamp(epoch_time)
    diff = current_time - datetimet

    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    months = days / 30
    years = days / 365

    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif minutes < 60:
        return f"{int(minutes)} minutes ago"
    elif hours < 24:
        return f"{int(hours)} hours ago"
    elif days < 30:
        return f"{int(days)} days ago"
    elif days < 365:
        return f"{int(months)} months ago"
    else:
        return f"{int(years)} years ago"
    
def epoch_to_time(epoch_time):
    if epoch_time == 0:
        return ""
    
    return datetime.fromtimestamp(epoch_time).strftime("%Y %m")