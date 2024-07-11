from functools import wraps
from flask import abort
from flask_login import current_user
from .models import AccessLevel

def access_required(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.has_access_level(access_level):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator