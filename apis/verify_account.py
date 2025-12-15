from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

# standard python libaryes
import time

# other python files
import x

from app import app

@app.get("/verify-account")
def view_verify_account():
    try:
        user_verification_key = x.validate_uuid4_without_dashes()
        user_verified_at = int(time.time())

        db, cursor = x.db()
        db.start_transaction()
        q = "SELECT user_fk FROM not_verifyed_accounts WHERE uuid = %s"
        cursor.execute(q, (user_verification_key,))

        user_fk = cursor.fetchone()["user_fk"]

        q = "DELETE FROM not_verifyed_accounts WHERE uuid = %s"
        cursor.execute(q, (user_verification_key,))

        q = "UPDATE users SET user_varified_at = %s WHERE user_pk = %s" 
        cursor.execute(q, (user_verified_at, user_fk))
        db.commit()

        return redirect(url_for('login'))
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()  

        # System or developer error
        return x.lans('cannot_verify_user')

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()