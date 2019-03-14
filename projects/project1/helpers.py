from flask import redirect, render_template, session, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("##################################################################")
        print(session.get("user_id"))
        if session.get("user_id") is None:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function