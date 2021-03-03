from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import Twidder.server


def run_server():
    http_server = WSGIServer(('',5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()

if __name__ == "__main__":
    run_server()
