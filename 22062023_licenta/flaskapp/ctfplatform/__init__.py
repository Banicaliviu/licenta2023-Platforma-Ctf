from flask import Flask
import time

app = Flask(__name__)
app.config.update(
    {
        "SECRET_KEY": "XlBGtHzPOefRKjiEB9yTcQS0WBHllAcx",
        "TESTING": True,
        "DEBUG": True,
        "OIDC_CLIENT_SECRETS": "auth.json",
        "OIDC_ID_TOKEN_COOKIE_SECURE": False,
        "OIDC_REQUIRE_VERIFIED_EMAIL": False,
        "OIDC_USER_INFO_ENABLED": True,
        "OIDC_OPENID_REALM": "flask-app",
        "OIDC_SCOPES": ["openid", "email", "profile"],
        "OIDC_TOKEN_TYPE_HINT": "access_token",
        "OIDC_INTROSPECTION_AUTH_METHOD": "client_secret_post"
        # 'OIDC_INTROSPECTION_AUTH_METHOD': 'bearer'
    }
)

from ctfplatform.db_create import create_db

create_db()

from ctfplatform.auth import auth_bp
from ctfplatform.main import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
