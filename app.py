from flask import Flask, render_template

from google_sheet import SHEET_NAME, get_next_feeding_time

app = Flask(__name__)


@app.route("/")
def index():
    # next_feeding = get_next_feeding_time()
    # next_feeding = 11
    # return render_template("index.html", next_feeding=next_feeding)
    return render_template("index.html", next_feeding=SHEET_NAME)
