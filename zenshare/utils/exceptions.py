"""ZenShare exceptions."""


class ZenShareError(Exception):
    """Base exception for ZenShare errors."""


class ConfigurationError(ZenShareError):
    """Raised when configuration cannot be loaded or validated."""


class StateError(ZenShareError):
    """Raised when state cannot be loaded, saved, or restored."""


class WindowsOperationError(ZenShareError):
    """Raised when a Windows-specific operation fails."""