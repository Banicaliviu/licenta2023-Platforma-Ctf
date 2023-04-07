from flask import Flask

app = Flask(__name__)
app.secret_key = "CTFPlatform"

from ctfplatform.auth import auth_bp
from ctfplatform.main import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)