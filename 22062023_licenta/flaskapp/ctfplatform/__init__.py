from flask import Flask
import time


app = Flask(__name__)

from ctfplatform.db_create import create_db

create_db()

from ctfplatform.auth import auth_bp
from ctfplatform.main import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
