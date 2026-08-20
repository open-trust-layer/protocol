"""Built-in conformance adapters."""

from .broken import BrokenAdapter
from .m22 import ReferenceAdapter

__all__ = ["BrokenAdapter", "ReferenceAdapter"]
