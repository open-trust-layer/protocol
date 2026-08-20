"""Built-in conformance adapters."""

from .broken import BrokenAdapter
from .m23 import ReferenceAdapter

__all__ = ["BrokenAdapter", "ReferenceAdapter"]
