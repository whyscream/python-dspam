# SPDX-License-Identifier: BSD-3-Clause

"""
Custom type annotations for dspam.
"""

from collections.abc import Mapping, Sequence
from typing import Literal

type LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

type Metadata = Mapping[str, str | Sequence[str]]
"""Metadata as produced by a parser."""

type Token = str
"""A single token as produced by a tokenizer."""

type TokenList = list[Token]
"""A list of Tokens as produced by a tokenizer."""

Verdict = Literal["innocent", "spam"]
"""Outcome of a classification."""
