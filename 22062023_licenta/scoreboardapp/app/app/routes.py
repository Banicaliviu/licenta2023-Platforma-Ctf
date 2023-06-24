from app import app

@app.route("/get_scoreboard")
def get_scoreboard():
    scoreboard = []
    return scoreboard