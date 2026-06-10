import email
import email.policy
from email.parser import Parser as PyEmailParser
from email.message import EmailMessage
from typing import cast

from anyio import AsyncFile

from dspam.exceptions import DspamParseError
from dspam.parse import Parser, ParseResult
from dspam.types import Metadata


class EmailParser(Parser):
    """
    A parser for email messages that extracts the email body and metadata such as sender, recipient, subject, and date.

    The email body and metadata are decoded into plain text, removing UTF-8 encoding and any email-specific formatting.
    The metadata is returned as a dictionary with keys corresponding to the email headers.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, fp: AsyncFile[str]) -> ParseResult:
        # Bridge async AsyncFile to sync file-like object for email.parser
        file_content = await fp.read()
        message_parser = PyEmailParser(policy=email.policy.default, _class=EmailMessage)
        message = cast(EmailMessage, message_parser.parsestr(file_content))  # type: ignore[redundant-cast]
        if message is None:
            raise DspamParseError("Failed to parse email")
        content = self.parse_body(message)

        metadata = self.parse_headers(message)
        return ParseResult(content, metadata)

    @staticmethod
    def parse_body(message: EmailMessage) -> str:
        """Extract the decoded text/plain body without message headers."""
        if message.is_multipart():
            body_part = message.get_body(preferencelist=("plain",))
            if body_part is None:
                raise DspamParseError("Email does not contain a text/plain body")
            content = body_part.get_content()
        else:
            if message.get_content_type() != "text/plain":
                raise DspamParseError("Only text/plain email messages are supported")
            content = message.get_content()

        if not isinstance(content, str):
            raise DspamParseError("Failed to decode email body as text")

        return content

    @staticmethod
    def parse_headers(message: EmailMessage) -> Metadata:
        """Extract metadata from email headers"""
        headers = {}
        for header_name in message.keys():
            header_value = message.get_all(header_name)
            if header_value is None:
                continue
            if len(header_value) == 1:
                headers[header_name] = header_value[0]
            else:
                headers[header_name] = header_value
        return headers
