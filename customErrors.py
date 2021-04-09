class Error(Exception):
    """Base Error class"""
    pass

class MalformedEquationError(Error):
    pass

class DegreeTooHighError(Error):
    pass
