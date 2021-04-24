"""Exceptions to be used in app"""


class ClientError(Exception):
    """Exception caught by websocket receive() handler"""

    def __init__(self, code, message):
        super(ClientError, self).__init__(code)
        self.code = code
        if message:
            self.message = message
