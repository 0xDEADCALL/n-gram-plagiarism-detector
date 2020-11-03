class Error(Exception):
    # Base class for errors
    pass


class NotPurePathError(Error):
    # Exception that is raised when a filepath is not a PurePath
    def __init__(self, message="Only PurePaths are allowed"):
        self.message = message
        super().__init__(self.message)


class NGramOrderNotSpecified(Error):
    # Exception raised when the
    def __init__(self, message="If not loading from .ngram file, order must be specified"):
        self.message = message
        super().__init__(self.message)
