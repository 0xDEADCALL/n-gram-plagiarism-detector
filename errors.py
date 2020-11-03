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


class NGramUnknownCoefficient(Error):
    # Exception raised when an unknown type of coefficient is specified
    def __init__(self, message="Unknown coefficient type the only ones allowed are> 'jaccard' or 'containment'"):
        self.message = message
        super().__init__(self.message)


class NGramNoInput(Error):
    # Exception raised when no input is passed to NGram object
    def __init__(self, message="A filepath or str must be passed to NGram"):
        self.message = message
        super().__init__(self.message)


class PathNotSpecified(Error):
    # Exception raised when no path is specified to save method
    def __init__(self, message="alt_path must be specified if object is generated from string"):
        self.message = message
        super().__init__(self.message)


class DepRelNoInput(Error):
    # Exception raised when no input is passed to NGram object
    def __init__(self, message="A filepath or str must be passed to DependecyRelations"):
        self.message = message
        super().__init__(self.message)
