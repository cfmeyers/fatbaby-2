from random import randint

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    next_feeding = randint(0, 10)
    return render_template("index.html", next_feeding=next_feeding)
