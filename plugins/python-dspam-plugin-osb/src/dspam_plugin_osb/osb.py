# SPDX-License-Identifier: BSD-3-Clause

import logging
from collections.abc import Iterator
from functools import partial

from dspam.settings import TokenizerSettings
from dspam.tokenize import (
    METADATA_IGNORE_DELIMITERS,
    Tokenizer,
    get_homoglyph_delimiters,
    tokenize_metadata,
    word_tokenize_content,
)
from dspam.types import Metadata, Token, TokenList

logger = logging.getLogger(__name__)


class OsbTokenizer(Tokenizer):
    API_VERSION = "1.0"

    SPARSE_WINDOW_SIZE = 5
    """The size of the sliding window for generating OSB tokens."""

    TOKEN_SEPARATOR: str = "+"  # noqa: S105
    """The separator to use between terms in OSB tokens."""

    OSB_TOKEN_PLACEHOLDER = "#"  # noqa: S105
    """The placeholder for skipped terms in an OSB token"""

    def __init__(self, settings: TokenizerSettings) -> None:
        super().__init__(settings)

    async def __call__(self, content: str, metadata: Metadata) -> TokenList:
        """Tokenize content and metadata into OSB tokens."""
        metadata_tokens = self.osb_tokenize_metadata(metadata)
        content_tokens = self.osb_tokenize_content(content)
        return metadata_tokens + content_tokens

    def osb_tokenize_content(self, content: str, ignore_delimiters: str = "") -> TokenList:
        """
        Tokenize a content string into OSB tokens.

        First, use the `WordTokenizer` to extract word tokens from the content.
        Then apply the OSB sliding window algorithm and generate OSB tokens for each window.
        """
        word_tokens = self.get_word_tokens(content, ignore_delimiters)
        osb_tokens = []
        # Prepopulate the token lists
        window_size = min(len(word_tokens), self.SPARSE_WINDOW_SIZE)
        window_terms = word_tokens[: window_size - 1]
        word_tokens = word_tokens[window_size - 1 :]

        while True:
            # Remove the first window token if needed
            if len(window_terms) >= self.SPARSE_WINDOW_SIZE:
                removed = window_terms.pop(0)
                logger.debug(f"Dropped window term {removed}")
            # Append window token if available
            if len(window_terms) < self.SPARSE_WINDOW_SIZE:
                try:
                    window_token = word_tokens.pop(0)
                    logger.debug(f"Appended window term {window_token}")
                    window_terms.append(window_token)
                except IndexError:
                    logger.debug("No more terms to append, processing complete")
                    break

                for token in self.get_osb_tokens(window_terms):
                    osb_tokens.append(token)

        return osb_tokens

    def get_osb_tokens(self, word_tokens: TokenList) -> Iterator[Token]:
        """
        Generate OSB tokens from a list of word tokens.

        The list of word tokens is considered as the non-sliding window.
        """
        window_size = len(word_tokens)
        for idx in range(1, window_size, 1):
            # Generate a single OSB token
            osb_token_terms = []
            for term_idx, term in enumerate(word_tokens, 1):
                if term_idx == idx:
                    # Append the first term
                    osb_token_terms.append(term)
                    logger.debug(f"Appending start term {term}")
                elif osb_token_terms and term_idx == window_size:
                    # Append last term only when we already have other terms
                    logger.debug(f"Appending end term {term}")
                    osb_token_terms.append(term)
                elif osb_token_terms:
                    # Append placeholders only when we already have other terms
                    logger.debug(f"Appending placeholder for term {term}")
                    osb_token_terms.append(self.OSB_TOKEN_PLACEHOLDER)

            osb_token = self.TOKEN_SEPARATOR.join(osb_token_terms)
            logger.debug(f"Generated OSB token: {osb_token}")
            yield osb_token

    def osb_tokenize_metadata(self, metadata: Metadata) -> TokenList:
        """Tokenize metadata into OSB tokens."""
        tokenizer = partial(self.osb_tokenize_content, ignore_delimiters=METADATA_IGNORE_DELIMITERS)
        return list(tokenize_metadata(metadata, tokenizer))

    def get_word_tokens(self, content: str, ignore_delimiters: str = "") -> list[str]:
        """Tokenize content into word tokens."""
        delimiters = "".join([d for d in self.settings.delimiters if d not in ignore_delimiters])
        delimiters += get_homoglyph_delimiters(delimiters)

        return word_tokenize_content(content, delimiters)
