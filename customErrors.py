class Error(Exception):
    """Base Error class"""
    pass

class UsageError(Error):
    pass

class MalformedEquationError(Error):
    pass