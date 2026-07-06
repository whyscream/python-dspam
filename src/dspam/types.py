# SPDX-License-Identifier: BSD-3-Clause

"""
Custom type annotations for dspam.
"""

from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Literal


class Classification(StrEnum):
    """Outcome of a classification or token categorization."""

    INNOCENT = "innocent"
    SPAM = "spam"
    UNKNOWN = "unknown"


type LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

type Metadata = Mapping[str, str | Sequence[str]]
"""Metadata as produced by a parser."""


class PluginGroup(StrEnum):
    """The available plugin groups"""

    PARSER = "parser"
    TOKENIZER = "tokenizer"
    CLASSIFIER = "classifier"
    TRAINER = "trainer"
    STORAGE = "storage"


type Token = str
"""A single token as produced by a tokenizer."""

type TokenList = list[Token]
"""A list of Tokens as produced by a tokenizer."""
