# SPDX-License-Identifier: BSD-3-Clause

import logging

from dspam.settings import TokenizerSettings
from dspam.tokenize import Tokenizer, WordTokenizer
from dspam.types import Metadata, TokenList

logger = logging.getLogger(__name__)


class OsbTokenizer(Tokenizer):
    API_VERSION = "1.0"

    SPARSE_WINDOW_SIZE = 5
    """The size of the sliding window for generating OSB tokens."""

    TOKEN_SEPARATOR: str = "+"  # noqa: S105
    """The separator to use between terms in OSB tokens."""

    OSB_TOKEN_PLACEHOLDER = "#"  # noqa: S105
    """The placeholder for skipped terms in an OSB token"""

    word_tokenizer: WordTokenizer

    def __init__(self, settings: TokenizerSettings) -> None:
        super().__init__(settings)

        self.word_tokenizer = WordTokenizer(self.settings)

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
                window_token = word_tokens.pop(0) if word_tokens else None
                if window_token:
                    logger.debug(f"Appended window term {window_token}")
                    window_terms.append(window_token)
                else:
                    logger.debug("No more terms to append, processing complete")
                    break

            for idx in range(1, window_size, 1):
                # Generate a single OSB token
                osb_token_terms = []
                for term_idx, term in enumerate(window_terms, 1):
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
                osb_tokens.append(osb_token)

        return osb_tokens

    def osb_tokenize_metadata(self, metadata: Metadata) -> TokenList:
        """Tokenize metadata into OSB tokens."""
        metadata_tokens = []
        for key, value in metadata.items():
            if isinstance(value, str):
                value = [value]

            for item in value:
                value_tokens = self.osb_tokenize_content(
                    item, ignore_delimiters=self.word_tokenizer.METADATA_IGNORE_DELIMITERS
                )
                for value_token in value_tokens:
                    metadata_tokens.append(f"{key}{self.word_tokenizer.METADATA_TOKEN_SEPARATOR}{value_token}")

        return metadata_tokens

    def get_word_tokens(self, content: str, ignore_delimiters: str = "") -> list[str]:
        """Tokenize content into word tokens."""
        return self.word_tokenizer.tokenize_content(content, ignore_delimiters)
