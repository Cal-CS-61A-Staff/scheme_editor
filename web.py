from flask import Flask, render_template, request

import scheme

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/process2", methods=["POST"])
def receive():
    code = request.form["code"]
    scheme.string_exec([code])
    return index()