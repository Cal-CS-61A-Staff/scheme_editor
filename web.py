from flask import Flask, render_template, request, jsonify

import gui
import scheme
from runtime_limiter import limiter, TimeLimitException
from scheme_exceptions import SchemeError

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/process2", methods=["POST"])
def receive():
    code = request.form.getlist("code[]")
    print("Received:", code)
    skip_tree = request.form.get("skip_tree")
    print(skip_tree)
    skip_tree = (skip_tree == "true")
    gui.logger.new_query(skip_tree)
    try:
        limiter(3000, scheme.string_exec, code, gui.logger.out)
    except SchemeError as e:
        gui.logger.out(e)
    except TimeLimitException:
        gui.logger.out("Time limit exceeded. Try disabling the substitution visualizer (top checkbox) for increased performance.")
    except Exception as e:
        raise
        gui.logger.out(e)

    out = gui.logger.export()
    # print(out)
    return jsonify(out)

