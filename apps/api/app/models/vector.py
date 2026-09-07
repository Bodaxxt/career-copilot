"""
Vector type support for PostgreSQL pgvector extension.
يدعم نوع Vector لتخزين Embeddings في PostgreSQL.
"""

from typing import Any
from sqlalchemy.types import UserDefinedType

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Fallback definition in case pgvector is not installed yet
    class Vector(UserDefinedType):
        """Custom SQLAlchemy Type for pgvector Vector."""

        cache_ok = True

        def __init__(self, dim: int = 1536):
            self.dim = dim

        def get_col_spec(self, **kw: Any) -> str:
            return f"vector({self.dim})"


__all__ = ["Vector"]
