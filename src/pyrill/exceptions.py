"""
Exceptions for PyRill client
"""


class RillError(Exception):
    """Base exception for all Rill client errors"""
    pass


class RillAuthError(RillError):
    """Authentication related errors"""
    pass


class RillAPIError(RillError):
    """REST API related errors"""

    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class RillCLIError(RillError):
    """CLI execution related errors"""

    def __init__(self, message, return_code=None, stderr=None):
        super().__init__(message)
        self.return_code = return_code
        self.stderr = stderr
