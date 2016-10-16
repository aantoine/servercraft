import random
import string

from werkzeug.security import generate_password_hash, \
    check_password_hash
from functools import wraps
from models import Config, get_without_failing
from flask import redirect, url_for, request, make_response, session


class Auth:
    def __init__(self):
        self.config = None

    def load(self):
        self.config = dict(
            CONFIG_PASSWORD=self.get_stored_pw()
        )

    @staticmethod
    def get_random_token():
        return ''.join(random.choice(string.lowercase) for _ in range(32))

    def set_password(self, password):
        _config = self._get_config()
        _config.value = generate_password_hash(password)
        _config.save()
        self.config['CONFIG_PASSWORD'] = _config.value

    def check_password(self, password):
        if self.config.get('CONFIG_PASSWORD', None) is None:
            return False
        return check_password_hash(self.config['CONFIG_PASSWORD'], password)

    @staticmethod
    def get_stored_pw():
        _config = get_without_failing(Config, (Config.name == 'password'), None)
        if _config is None:
            return None
        return _config.value

    @staticmethod
    def _get_config():
        _config, created = Config.get_or_create(name='password', defaults={'value': 'dummy'})
        return _config

    def is_authenticated(self):
        if self.config.get('CONFIG_PASSWORD', None) \
                and not session.get('logged_in', False):
            return False
        else:
            return True

    def login_required(self, func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            if self.is_authenticated():
                return func(*args, **kwargs)
            next_url = request.url
            login_url = '%s?next=%s' % (url_for('login'), next_url)
            return redirect(login_url)
        return func_wrapper

    def check_logged_in(self, func):
        @wraps(func)
        def func_wrapper():
            if self.is_authenticated():
                return func(True)
            return func(False)

        return func_wrapper

    def login(self, redirect_page):
        def decorator(func):
            @wraps(func)
            def func_wrapper():
                if self.is_authenticated():
                    return redirect(url_for(redirect_page))
                if request.method == "GET":
                    return func(_next=request.args.get('next', None))
                if self.check_password(request.form.get('password', '')):
                    if request.form.get('next', None) is not None:
                        resp = redirect(request.form.get('next', None))
                    else:
                        resp = redirect(url_for(redirect_page))
                    session['logged_in'] = True
                    return resp
                else:
                    return func(request.form.get('next', None))

            return func_wrapper

        return decorator

    @staticmethod
    def logout(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            resp = func(*args, **kwargs)
            session['logged_in'] = False
            return resp

        return func_wrapper

    def setup_required(self, config_page):
        def decorator(func):
            @wraps(func)
            def setup_required_func_wrapper(*args, **kwargs):
                if self.config.get('CONFIG_PASSWORD', None) is None:
                    return make_response(redirect(url_for(config_page)))
                else:
                    return func(*args, **kwargs)

            return setup_required_func_wrapper

        return decorator

    def post_credentials(self, pw_field):
        def decorator(func):
            @wraps(func)
            def func_wrapper(*args, **kwargs):
                psw = request.form.get(pw_field, None)
                pw_changed = not self.check_password(psw)
                # if self.config.get('CONFIG_PASSWORD', None) is None:
                #     install_first_configuration()
                if pw_changed:
                    self.set_password(psw)
                    session['logged_in'] = True
                return func(*args, **kwargs)

            return func_wrapper

        return decorator


auth = Auth()
