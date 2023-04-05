from flask import Flask

app = Flask(__name__)
app.secret_key = "CTFPlatform"

from ctfplatform import routes