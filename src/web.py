import json

from flask import Flask, render_template, request, jsonify

from src import execution, database, gui
from src.runtime_limiter import limiter, TimeLimitException
from src.scheme_exceptions import SchemeError

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html", start_data=json.dumps({}))


@app.route("/<code>")
def lookup(code):
    val = database.load(code)
    if val is None:
        return index()
    return render_template("index.html",
                           start_data=repr(json.dumps({"code": eval(val[0]),
                                                       "skip_tree": bool(val[1]),
                                                       "hide_return_frames": bool(val[2])})))


@app.route("/process2", methods=["POST"])
def receive():
    code = request.form.getlist("code[]")
    skip_tree = request.form.get("skip_tree") == "true"
    hide_return_frames = request.form.get("hide_return_frames") == "true"
    print(request.form.get("hide_return_frames"))
    return handle(code, skip_tree, hide_return_frames)


def handle(code, skip_tree, hide_return_frames):
    gui.logger.setID(database.save(code, skip_tree, hide_return_frames))
    gui.logger.new_query(skip_tree, hide_return_frames)
    try:
        limiter(3, execution.string_exec, code, gui.logger.out)
    except SchemeError as e:
        gui.logger.out(e)
    except TimeLimitException:
        gui.logger.out("Time limit exceeded. Try disabling the substitution visualizer (top checkbox) for increased "
                       "performance.")
    except Exception as e:
        raise
        gui.logger.out(e)

    out = gui.logger.export()
    return jsonify(out)

