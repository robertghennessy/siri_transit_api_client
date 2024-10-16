"""
Defines exceptions that are thrown by the api client.
"""


class ApiError(Exception):
    """Represents an exception returned by the remote API."""

    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def __str__(self):
        if self.message is None:
            return str(self.status)
        else:
            return "%s (%s)" % (self.status, self.message)


class TransportError(Exception):
    """Something went wrong while trying to execute the request."""

    def __init__(self, base_exception=None):
        self.base_exception = base_exception

    def __str__(self):
        if self.base_exception:
            return str(self.base_exception)
        return "An unknown error occurred."


class HTTPError(TransportError):
    """An unexpected HTTP error occurred."""

    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return "HTTP Error: %d" % self.status_code


class Timeout(Exception):
    """The request timed out."""

    pass


class RetriableRequest(Exception):
    """Signifies that the request can be retried."""

    pass


class OverQueryLimit(ApiError, RetriableRequest):
    """Signifies that the request failed because the client exceeded its query rate limit.
    Normally we treat this as a retriable condition, but we allow the calling code to specify that these requests should
    not be retried.
    """

    pass
