"""Exception hierarchy for the OLP reference implementation."""

from __future__ import annotations


class OLPError(Exception):
    """Base class for reference implementation errors."""


class ConformanceError(OLPError):
    """Raised when an abstract OLP object violates a normative data-model rule."""

    def __init__(self, message: str, *, code: str = "NONCONFORMING") -> None:
        super().__init__(message)
        self.code = code


class EncodingError(OLPError):
    """Raised when a value cannot be encoded by the required deterministic CBOR profile."""


class ResourceLimitError(EncodingError):
    """Raised when implementation resource limits are exceeded."""


class UnsupportedFeatureError(OLPError):
    """Raised by producer-side APIs when a requested feature is not implemented."""

    def __init__(self, message: str, *, code: str = "UNSUPPORTED") -> None:
        super().__init__(message)
        self.code = code


class KeyMaterialError(OLPError):
    """Raised when signing or verification key material is malformed."""
