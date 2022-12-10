from flask import Flask, render_template

from google_sheet import SHEET_NAME, get_baby_update

app = Flask(__name__)


@app.route("/")
def index():
    baby_update = get_baby_update()
    return render_template(
        "index.html",
        baby_update=baby_update,
    )
