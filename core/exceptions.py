class InvalidInputException(Exception):
    # Base class for all our exceptions.  All exceptions we generate should
    # either use or subclass this.

    def __init__(self, error_msg):
        self.error_msg = error_msg

    def __str__(self):
        return str(error_msg)
