class APIError(Exception):
    """
    .. versionadded:: 0.2.5


    This is raised on all other http errors and will always return http error code, reason for fail
    (if a reason is given otherwise None), url which failed
    """
    pass

class NotModified(APIError):
    """
    This is raised when using the last modified option and nothing changed, since last request
    """
    pass

class NotFound(APIError):
    """
    This is raised on 404 Errors
    """
    pass