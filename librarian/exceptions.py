class LibrarianError(Exception):
    pass


class RateLimitError(LibrarianError):
    pass


class ProviderUnavailableError(LibrarianError):
    pass


class ProjectNotInitialisedError(LibrarianError):
    pass


class SafetyBoundaryError(LibrarianError):
    pass


class ChunkNotFoundError(LibrarianError):
    pass
