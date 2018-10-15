from flask import Flask, render_template, request, jsonify

import gui
import scheme

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/process2", methods=["POST"])
def receive():
    code = request.form["code"]
    gui.logger.reset()
    scheme.string_exec([code])
    out = gui.logger.export()
    print("Returning:", out)
    return jsonify(out)

