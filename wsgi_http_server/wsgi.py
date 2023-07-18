import io
import socket
import sys


class WSGIServer:
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1

    def __init__(self, server_address):
        self.listen_socket = socket.socket(
            self.address_family, self.socket_type
        )

        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind
        self.listen_socket.bind(server_address)

        # listen
        self.listen_socket.listen(self.request_queue_size)

        # Get server hostname and port
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

        # Headers set by framework/web-application
        self.headers_set = []

    def set_app(self, application):
        self.application = application


    def server_forever(self):
        listen_socket = self.listen_socket
        while True:
            # new client connection
            self.client_connection, client_address = listen_socket.accept()

            # Handle one request and close client connection. Then loop
            # over to wait for another client connection
            self.handle_one_request()
    
    def handle_one_request(self):
        self.request_data = self.client_connection.recv(2048)
        self.request_data = self.request_data.decode('utf-8')
        print(self.request_data)
        # print request data to the console
        print('Request to server: \n' + ''.join(
            f'--> {line}\n' for line in self.request_data.splitlines()
        ))

        self.parse_request(self.request_data)

        # Construct environment dictionary using request data
        env = self.get_environ()

        # Call our application with env and default response headers
        result = self.application(env, self.start_response)

        # Construct a response and send it back to the client
        self.finish_response(result)

    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip('\r\n')

        # Break down the request lines into components
        (
            self.request_method,
            self.path,
            self.request_version
        ) = request_line.split()

    def get_environ(self):
        env = {}

        # Required WSGI variables
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = io.StringIO(self.request_data)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False
        # Required CGI variables
        env['REQUEST_METHOD'] = self.request_method # GET
        env['PATH_INFO'] = self.path                # /page
        env['SERVER_NAME'] = self.server_name       # localhost
        env['SERVER_PORT'] = str(self.server_port)  # 8888

        return env
    
    def start_response(self, status, response_headers, exc_info=None):
        # Add necessary server headers
        server_headers = [
            ('Date', 'Mon, 15 Jul 2019 5:54:48 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]
        # To adhere to WSGI specification the start_response must return
        # a 'write' callable. We simplicity's sake we'll ignore that detail
        # for now.
        return self.finish_response

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = f'HTTP/1.1 {status}\r\n'
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data.decode('utf-8')
            print('Response to client: \n' + ''.join(
                    f'<-- {line}\n' for line in response.splitlines()
            ))
            response_bytes = response.encode()
            self.client_connection.sendall(response_bytes)
        finally:
            self.client_connection.close()
            print('The connection is closed')


SERVER_ADDRESS = (HOST, PORT) = '127.0.0.1', 8888


def make_server(server_address, application):
    server = WSGIServer(server_address=server_address)
    server.set_app(application=application)
    return server


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    print(sys.argv)
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print(f'WSGIServer: Running HTTP-server on port {PORT} ...\n')
    httpd.server_forever()
