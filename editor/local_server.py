import http.server
import json
import signal
import socketserver
import sys
import urllib.parse
from http import HTTPStatus

from editor.formatter import prettify
from editor import execution, gui
from editor.runtime_limiter import TimeLimitException, limiter
from editor.scheme_exceptions import SchemeError

PORT = 8000

file = None


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        raw_data = self.rfile.read(content_length)
        data = urllib.parse.parse_qs(raw_data)
        path = urllib.parse.unquote(self.path)
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
            file.truncate(0)
            file.seek(0)
            file.write("\n".join(code))
            file.flush()
            self.send_response(HTTPStatus.OK, 'test')
            self.send_header("Content-type", "application/JSON")
            self.end_headers()
            self.wfile.write(bytes("success", "utf-8"))
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

    def do_GET(self):
        self.send_response(HTTPStatus.OK, 'test')
        path = "scheme/static/" + urllib.parse.unquote(self.path)[1:]
        if path[-4:] == ".css":
            self.send_header("Content-type", "text/css")
        self.end_headers()
        code = [""]
        if path == "scheme/static/":
            path = "scheme/static/index.html"
            if file is not None:
                file.seek(0)
                code = ["".join(file)]
                print(code, file)
        try:
            with open(path, "rb") as f:  # lol better make sure that port is closed
                self.wfile.write(f.read()
                                 .replace(b"<START_DATA>",
                                          bytes(repr(json.dumps({"code": code,
                                                            "skip_tree": True,
                                                            "hide_return_frames": True})),
                                                "utf-8")))
        except Exception as e:
            print(e)

    def log_message(self, *args, **kwargs):
        pass


def handle(code, curr_i, curr_f, global_frame_id):
    # file.truncate(0)
    # file.seek(0)
    # file.write("\n".join(code))
    # file.flush()
    try:
        gui.logger.new_query(curr_i, curr_f)
        if global_frame_id == -1:
            execution.string_exec(code, gui.logger.out)
        else:
            execution.string_exec(code, gui.logger.out, gui.logger.frame_lookup[global_frame_id].base)
        # limiter(3, execution.string_exec, code, gui.logger.out)
    except Exception as e:
        raise

    out = gui.logger.export()
    return json.dumps(out)


def instant(code, global_frame_id):
    gui.logger.new_query()
    try:
        gui.logger.preview_mode(True)
        limiter(0.3, execution.string_exec, code, gui.logger.out, gui.logger.frame_lookup[global_frame_id].base)
    except (SchemeError, ZeroDivisionError) as e:
        gui.logger.out(e)
    except TimeLimitException:
        pass
    except Exception as e:
        raise
    finally:
        gui.logger.preview_mode(False)
    return json.dumps({"success": True, "content": gui.logger.export()["out"]})


def exit_handler(signal, frame):
    print(" - Ctrl+C pressed")
    print("Shutting down server - all unsaved work will be lost")
    file.close()
    sys.exit(0)


signal.signal(signal.SIGINT, exit_handler)


def start(file_arg=None):
    global file
    file = file_arg
    print(f"http://localhost:{PORT}")
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("localhost", PORT), Handler) as httpd:
        httpd.serve_forever()
