import json

from flask import Flask, render_template, request, jsonify

import database
import gui
import scheme
from runtime_limiter import limiter, TimeLimitException
from scheme_exceptions import SchemeError

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html", start_data=json.dumps({}))


@app.route("/<code>")
def lookup(code):
    val = database.load(code)
    if val is None:
        return index()
    return render_template("index.html", start_data=repr(json.dumps({"code": eval(val[0]), "skip_tree": bool(val[1])})))


@app.route("/process2", methods=["POST"])
def receive():
    code = request.form.getlist("code[]")
    skip_tree = request.form.get("skip_tree")
    skip_tree = (skip_tree == "true")
    return handle(code, skip_tree)


def handle(code, skip_tree):
    gui.logger.setID(database.save(code, skip_tree))
    gui.logger.new_query(skip_tree)
    try:
        limiter(3, scheme.string_exec, code, gui.logger.out)
    except SchemeError as e:
        gui.logger.out(e)
    except TimeLimitException:
        gui.logger.out("Time limit exceeded. Try disabling the substitution visualizer (top checkbox) for increased "
                       "performance.")
    except Exception as e:
        # raise
        gui.logger.out(e)

    out = gui.logger.export()
    return jsonify(out)

