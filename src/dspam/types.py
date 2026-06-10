"""
Custom type annotations for dspam.
"""

from collections.abc import Mapping, Sequence

type Metadata = Mapping[str, str | Sequence[str]]
"""Metadata as produced by a parser."""
