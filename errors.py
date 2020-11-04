class Error(Exception):
    # Base class for errors
    pass


class NotPurePathError(Error):
    # Exception that is raised when a filepath is not a PurePath
    def __init__(self, message="Only PurePaths are allowed"):
        self.message = message
        super().__init__(self.message)


class NGramUnknownCoefficient(Error):
    # Exception raised when an unknown type of coefficient is specified
    def __init__(self, message="Unknown coefficient type the only ones allowed are> 'jaccard' or 'containment'"):
        self.message = message
        super().__init__(self.message)


class DepRelNoInput(Error):
    # Exception raised when no input is passed to NGram object
    def __init__(self, message="A filepath or str must be passed to DependecyRelations"):
        self.message = message
        super().__init__(self.message)
