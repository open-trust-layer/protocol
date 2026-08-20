"""Built-in conformance adapters."""

from .broken import BrokenAdapter
from .m24 import ReferenceAdapter

__all__ = ["BrokenAdapter", "ReferenceAdapter"]
