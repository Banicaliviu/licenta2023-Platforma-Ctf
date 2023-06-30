from flask import Flask
import time


app = Flask(__name__)
app.config.update(
    SECRET_KEY='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
)

from ctfplatform.db_create import create_db

create_db()

from ctfplatform.auth import auth_bp
from ctfplatform.main import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
