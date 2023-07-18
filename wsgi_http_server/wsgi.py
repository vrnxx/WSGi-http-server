import io
import socket
import sys


class WSGIServer:
    """Class for working with user connections via the http/wsgi protocol.

    :param server_address: Tuple with 2 values. Hostname:str -
    `'localhost'` or `'127.0.0.1'`,
    `Port:int - 9000.`
    :type server_address: tuple, required.

    Attributes:
        request_queue_size  Queue of client connections to server-socket
        address_family      Address family for server-socket, default IPv4.
        socket_type         Type of server-socket, default TCP.
    """

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5

    def __init__(self, server_address):
        """
        Constructor method.
        """
        self.listen_socket = socket.socket(
            self.address_family, self.socket_type
        )

        # Set a reuse address.
        self.listen_socket.setsockopt(socket.SOL_SOCKET, 
                                      socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(server_address)
        self.listen_socket.listen(self.request_queue_size)

        # Get server hostname and port
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

        # Headers set by framework/web-application
        self.headers_set = []

    def set_app(self, application):
        """Set an application for WSGIServer instance.

        Args:
            application (Callable object): instance of choices
            `web-application`: `flask`, `django` ect.
        """

        self.application = application

    def server_forever(self):
        """Starts an infinite loop in which it accepts
        and processes client connections.

        For each client connection run hanlde_one_request function.
        """

        listen_socket = self.listen_socket
        while True:
            # new client connection
            self.client_connection, client_address = listen_socket.accept()

            self.handle_one_request()

    def handle_one_request(self):
        """Receives 2048 bytes of client request.
        Decrypts it and prints it to the console
        in a special format.

        Prepares request data for a response and sends it to the client using
        special environment variables.
        """
        self.request_data = self.client_connection.recv(2048)
        self.request_data = self.request_data.decode('utf-8')

        print('Request to server: \n' + ''.join(
            f'--> {line}\n' for line in self.request_data.splitlines()
        ))

        self.parse_request(self.request_data)

        # Construct environment dictionary using request data
        env = self.get_environ()

        # Call our application with env and default response headers
        result = self.application(env, self.start_response)

        # Send a response to client and close connection
        self.finish_response(result)

    def parse_request(self, text):
        """Parses the raw text of the request and
        takes the request method, path and protocol
        version from it.

        Args:
            text (str): Raw text of the request.
        """
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip('\r\n')

        (
            self.request_method,
            self.path,
            self.request_version
        ) = request_line.split()

    def get_environ(self):
        """Creates a new dict with required variables.

        Returns:
            dict: Key-value pairs with required variables for
            WSGI and CGI protocols.
        """
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
        env['REQUEST_METHOD'] = self.request_method
        env['PATH_INFO'] = self.path
        env['SERVER_NAME'] = self.server_name
        env['SERVER_PORT'] = str(self.server_port)

        return env

    def start_response(self, status, response_headers, exc_info=None):
        """Sets a default headers to response.

        Args:
            status (byte-string): HTTP response status
            response_headers (byte-string): HTTP response headers
            exc_info (byte-string, optional): Info for errors.
            Defaults to None.

        Returns:
            Callable object: link to finish_response method. It`s required
            returned value in WSGI protocol.
        """
        server_headers = [
            ('Date', 'Mon, 17 Jul 2023 5:54:48 GMT+3'),
            ('Server', 'WSGIServer 0.1'),
        ]
        self.headers_set = [status, response_headers + server_headers]

        return self.finish_response

    def finish_response(self, result):
        """Gets a byte string containing the response body
        for the client. Sets the headers for the response.
        Prints information about the response to the client
        to the console. Sends a response to the client and
        closes the connection.

        Args:
            result (byte-string): byte-string with `HTTP` `status`
            and `headers`.
        """
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


SERVER_ADDRESS = (HOST, PORT) = '127.0.0.1', 9000


def make_server(server_address, application):

    """Creates a WSGIServer instance
    with the given parameters.

    Args:
        server_address (tuple): Tuple with 2 values. Hostname:str -
        `'localhost'` or `'127.0.0.1'`,
        `Port:int - 9000.`
        application (callable object): instance of choices application.

    Returns:
        <class '__main__.WSGIServer'>: instance of WSGIServer class.
    """
    server = WSGIServer(server_address=server_address)
    server.set_app(application=application)
    return server


if __name__ == '__main__':
    """
    Entrypoint.

    Start WSGI http-server with choices web-application.
    """
    if len(sys.argv) < 2:
        sys.exit("""Provide a WSGI application object as module:callable\n""")
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print(f'WSGIServer: Running HTTP-server on port {PORT} ...\n')
    httpd.server_forever()
