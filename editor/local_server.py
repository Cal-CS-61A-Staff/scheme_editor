from http import server
import json
import signal
import socketserver
import sys
import urllib.parse
import webbrowser
import threading
from http import HTTPStatus

import execution
import log
from documentation import search
from execution_parser import strip_comments
from file_manager import get_scm_files, save, read_file, new_file
from formatter import prettify
from runtime_limiter import TimeLimitException, limiter
from scheme_exceptions import SchemeError, ParseError, TerminatedError

PORT = 8012

main_files = []

state = {}

import ctypes


def terminate_thread(thread):
    """Terminates a python thread from another thread.

    :param thread: a threading.Thread instance

    From https://stackoverflow.com/a/15274929/1549476 but I replaced SystemExit with KeyboardInterrupt
    """
    if not thread.isAlive():
        return

    exc = ctypes.py_object(TerminatedError)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class thread_state:
    def __init__(self):
        self.post_lock = threading.Lock()
        self.modify_current_thread_lock = threading.Lock()
        self.current_thread = None

    def cancel(self):
        with self.modify_current_thread_lock:
            if self.current_thread is not None:
                terminate_thread(self.current_thread)
                self.current_thread = None

    def run(self, target, *args):
        with self.post_lock:
            with self.modify_current_thread_lock:
                assert self.current_thread is None
                thread = self.current_thread = threading.Thread(target=target, args=args)
                thread.daemon = True
                thread.start()
            thread.join()
            with self.modify_current_thread_lock:
                assert self.current_thread is thread or self.current_thread is None
                self.current_thread = None


# singleton
thread_state = thread_state()


class Handler(server.BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Only one non-/cancel POST can happen at a time, the only reason this is threaded is to
            allow the /cancel command to work

        The state is represented as such:
            current_thread --> None if no thread is running, otherwise the thread handling the
                current POST command

        and any time we wish to modify the state, we use the lock post_lock
        """
        content_length = int(self.headers['Content-Length'])
        raw_data = self.rfile.read(content_length)
        data = urllib.parse.parse_qs(raw_data)
        path = urllib.parse.unquote(self.path)
        if path == "/cancel":
            thread_state.cancel()
        else:
            thread_state.run(self.handle_post_thread, data, path)

    def handle_post_thread(self, data, path):

        if b"code[]" not in data:
            data[b"code[]"] = [b""]

        if path == "/process2":
            code = [x.decode("utf-8") for x in data[b"code[]"]]
            curr_i = int(data[b"curr_i"][0])
            curr_f = int(data[b"curr_f"][0])
            global_frame_id = int(data[b"globalFrameID"][0])
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()
            self.wfile.write(bytes(handle(code, curr_i, curr_f, global_frame_id), "utf-8"))

        elif path == "/save":
            code = [x.decode("utf-8") for x in data[b"code[]"]]
            filename = data[b"filename"][0]
            do_save = data[b"do_save"][0] == b"true"
            if do_save:
                save(code, filename)
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"result": "success", "stripped": strip_comments(code)}), "utf-8"))

        elif path == "/instant":
            code = [x.decode("utf-8") for x in data[b"code[]"]]
            global_frame_id = int(data[b"globalFrameID"][0])
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()
            self.wfile.write(bytes(instant(code, global_frame_id), "utf-8"))

        elif path == "/reformat":
            code = [x.decode("utf-8") for x in data[b"code[]"]]
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"result": "success", "formatted": prettify(code)}), "utf-8"))

        elif path == "/test":
            from ok_interface import run_tests
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(run_tests()), "utf-8"))

        elif path == "/list_files":
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(get_scm_files()), "utf-8"))

        elif path == "/read_file":
            filename = data[b"filename"][0]
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(read_file(filename)), "utf-8"))

        elif path == "/new_file":
            filename = data[b"filename"][0].decode("utf-8")
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"success": new_file(filename)}), "utf-8"))

        elif path == "/save_state":
            global state
            for key, val in json.loads(data[b"state"][0].decode("utf-8")).items():
                if key == "states":
                    if "states" not in state:
                        state["states"] = val
                    else:
                        merge(state["states"], val)
                else:
                    state[key] = val
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()

        elif path == "/load_state":
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()
            if "states" not in state:
                self.wfile.write(b"fail")
            else:
                self.wfile.write(bytes(json.dumps(state), "utf-8"))

        elif path == "/documentation":
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()

            query = data.get(b"query", [b""])[0].decode("utf-8")
            self.wfile.write(bytes(json.dumps(search(query)), "utf-8"))

    def do_GET(self):
        self.send_response(HTTPStatus.OK, 'test')
        path = "editor/static/" + urllib.parse.unquote(self.path)[1:]

        if "scripts" in path and not path.endswith(".js"):
            path += ".js"

        if path.endswith(".css"):
            self.send_header("Content-type", "text/css")
        elif path.endswith(".js"):
            self.send_header("Content-type", "application/javascript")
        self.end_headers()
        if path == "editor/static/":
            path = "editor/static/index.html"
        try:
            with open(path, "rb") as f:  # lol better make sure that port is closed
                self.wfile.write(f.read()
                                 .replace(b"<START_DATA>",
                                          bytes(repr(json.dumps({"files": main_files})),
                                                "utf-8")))
        except Exception as e:
            print(e)
            # raise

    def log_message(self, *args, **kwargs):
        pass


def merge(states, new_states):
    for i, new_state in enumerate(new_states):
        if i == len(states):
            states.append(new_state)
        else:
            for key, val in new_state.items():
                states[i][key] = val


def handle(code, curr_i, curr_f, global_frame_id):
    try:
        global_frame = log.logger.frame_lookup.get(global_frame_id, None)
        log.logger.new_query(global_frame, curr_i, curr_f)
        if global_frame_id == -1:
            execution.string_exec(code, log.logger.out)
        else:
            execution.string_exec(code, log.logger.out, global_frame.base)
        # limiter(3, execution.string_exec, code, gui.logger.out)
    except ParseError as e:
        return json.dumps({"success": False, "out": [str(e)]})

    out = log.logger.export()
    return json.dumps(out)


def instant(code, global_frame_id):
    global_frame = log.logger.frame_lookup[global_frame_id]
    log.logger.new_query(global_frame)
    try:
        log.logger.preview_mode(True)
        limiter(0.3, execution.string_exec, code, log.logger.out, global_frame.base)
    except (SchemeError, ZeroDivisionError) as e:
        log.logger.out(e)
    except TimeLimitException:
        pass
    except Exception as e:
        raise
    finally:
        log.logger.preview_mode(False)
    return json.dumps({"success": True, "content": log.logger.export()["out"]})


def exit_handler(signal, frame):
    print(" - Ctrl+C pressed")
    print("Shutting down server - all unsaved work may be lost")
    print("Remember that you should run python ok in a separate terminal window, to avoid stopping the editor process.")
    thread_state.cancel()
    sys.exit(0)


signal.signal(signal.SIGINT, exit_handler)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, server.HTTPServer):
    pass


def start(file_args, port, open_browser):
    global main_files
    main_files = file_args
    global PORT
    PORT = port
    print(f"http://localhost:{PORT}")
    socketserver.TCPServer.allow_reuse_address = True
    httpd = ThreadedHTTPServer(("localhost", PORT), Handler)
    if open_browser:
        webbrowser.open(f"http://localhost:{PORT}", new=0, autoraise=True)
    httpd.serve_forever()
