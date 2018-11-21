import http.server
import json
import signal
import socketserver
import sys
import urllib.parse
from http import HTTPStatus

from scheme import execution, gui
from scheme.runtime_limiter import TimeLimitException
from scheme.scheme_exceptions import SchemeError

PORT = 8000


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        raw_data = self.rfile.read(content_length)
        data = urllib.parse.parse_qs(raw_data)
        code = [x.decode("utf-8") for x in data[b"code[]"]]
        skip_tree = data[b"skip_tree"] == b"true"
        skip_envs = data[b"skip_envs"][0] == b"true"
        hide_return_frames = data[b"hide_return_frames"][0] == b"true"
        self.send_response(HTTPStatus.OK, 'test')
        self.send_header("Content-type", "application/JSON")
        self.end_headers()
        self.wfile.write(bytes(handle(code, skip_tree, skip_envs, hide_return_frames), "utf-8"))

    def do_GET(self):
        self.send_response(HTTPStatus.OK, 'test')
        path = "scheme/static/" + urllib.parse.unquote(self.path)[1:]
        if path[-4:] == ".css":
            self.send_header("Content-type", "text/css")
        self.end_headers()
        if path == "scheme/static/":
            path = "scheme/static/index.html"
        try:
            with open(path, "rb") as f:  # lol better make sure that port is closed
                self.wfile.write(f.read().replace(b"<START_DATA>", b"{}"))
        except Exception as e:
            print(e)


def handle(code, skip_tree, skip_envs, hide_return_frames):
    gui.logger.new_query(skip_tree, skip_envs, hide_return_frames)
    print("cat")
    try:
        execution.string_exec(code, gui.logger.out)
        # limiter(3, execution.string_exec, code, gui.logger.out)
    except SchemeError as e:
        gui.logger.out(e)
    except TimeLimitException:
        gui.logger.out("Time limit exceeded. Try disabling the substitution visualizer (top checkbox) for increased "
                       "performance.")
    except Exception as e:
        raise

    out = gui.logger.export()
    return json.dumps(out)


def exit_handler(signal, frame):
    print(" - Ctrl+C pressed")
    print("Shutting down server - all unsaved work will be lost")
    sys.exit(0)


signal.signal(signal.SIGINT, exit_handler)


def start():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("localhost", PORT), Handler) as httpd:
        httpd.serve_forever()
