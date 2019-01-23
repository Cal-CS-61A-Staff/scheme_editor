import json
import os

 from flask import Flask, request

 import execution
import log
from documentation import search
from file_manager import get_scm_files, save, read_file
from formatter import prettify
from ok_interface import run_tests, parse_test_data
from runtime_limiter import TimeLimitException, limiter
from scheme_exceptions import SchemeError, ParseError


 main_file = "/hw10.scm"

 app = Flask(__name__)

 state = None


 @app.route("/process2", methods=["POST"])
def process2():
    code = request.form.getlist("code[]")
    curr_i = int(request.form.get("curr_i"))
    curr_f = int(request.form.get("curr_f"))
    global_frame_id = int(request.form.get("globalFrameID"))
    return handle(code, curr_i, curr_f, global_frame_id)


 @app.route("/save", methods=["POST"])
def save_handler():
    code = request.form.getlist("code[]")

     filename = request.form.get("filename")

     save(code, filename)

     return "success"


 @app.route("/instant", methods=["POST"])
def instant_handler():
    code = request.form.getlist("code[]")

     global_frame_id = int(request.form.get("globalFrameID"))

     return instant(code, global_frame_id)


 @app.route("/reformat", methods=["POST"])
def reformat_handler():
    code = request.form.getlist("code[]")

     return json.dumps({"result": "success",
                       "formatted": prettify(code)})


 @app.route("/test", methods=["POST"])
def test_handler():
    code = request.form.getlist("code[]")

     filename = request.form.get("filename")

     save(code, filename)

     return json.dumps(parse_test_data(run_tests()))


 @app.route("/list_files", methods=["POST"])
def list_files_handler():
    return json.dumps(get_scm_files())


 @app.route("/read_file", methods=["POST"])
def read_file_handler():
    filename = request.form.get("filename")

     return json.dumps(read_file(filename))


 @app.route("/save_state", methods=["POST"])
def save_state():
    global state
    state = request.form.get("state")


 @app.route("/load_state", methods=["POST"])
def load_state():
    if state is None:
        return "fail"
    else:
        return state


 @app.route("/documentation", methods=["POST"])
def documentation():
    query = request.form.get("query")
    return json.dumps(search(query))


 @app.route('/')
def do_GET():
    try:
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        with open(APP_ROOT + "/static/index.html", "rb") as f:  # lol better make sure that port is closed
            return f.read().replace(b"<START_DATA>", bytes(repr(json.dumps({"file": main_file})), "utf-8"))
    except Exception as e:
        raise


 def handle(code, curr_i, curr_f, global_frame_id):
    # file.truncate(0)
    # file.seek(0)
    # file.write("\n".join(code))
    # file.flush()
    try:
        log.logger.new_query(curr_i, curr_f)
        if global_frame_id == -1:
            execution.string_exec(code, log.logger.out)
        else:
            execution.string_exec(code, log.logger.out, log.logger.frame_lookup[global_frame_id].base)
        # limiter(3, execution.string_exec, code, gui.logger.out)
    except ParseError as e:
        return json.dumps({"success": False, "out": [str(e)]})

     out = log.logger.export()
    return json.dumps(out)


 def instant(code, global_frame_id):
    log.logger.new_query()
    try:
        log.logger.preview_mode(True)
        limiter(0.3, execution.string_exec, code, log.logger.out, log.logger.frame_lookup[global_frame_id].base)
    except (SchemeError, ZeroDivisionError) as e:
        log.logger.out(e)
    except TimeLimitException:
        pass
    except Exception as e:
        raise
    finally:
        log.logger.preview_mode(False)
    return json.dumps({"success": True, "content": log.logger.export()["out"]})
