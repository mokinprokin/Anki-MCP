class AnkiBaseException(Exception):
    """Base exception for all Anki service domain errors."""


class AnkiConnectionError(AnkiBaseException):
    """Raised when network connectivity to AnkiConnect fails or times out."""


class AnkiAPIError(AnkiBaseException):
    """Raised when AnkiConnect responds with an application-level error."""


class AnkiServiceNotInitializedError(AnkiBaseException):
    """Raised when attempting to execute requests on an uninitialized HTTP session."""
