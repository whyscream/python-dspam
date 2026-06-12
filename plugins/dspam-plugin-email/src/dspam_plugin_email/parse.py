import email
import email.policy
import html
import logging
import re
from email.parser import Parser as PyEmailParser
from email.message import EmailMessage, MIMEPart
from typing import cast

from anyio import AsyncFile

from dspam.exceptions import DspamParseError
from dspam.parse import Parser, ParseResult
from dspam.settings import ParserSettings
from dspam.types import Metadata

logger = logging.getLogger(__name__)


class EmailParserSettings(ParserSettings):
    ignore_headers: list[str] = []
    """
    Email headers to ignore during parsing.

    Forged headers from other spam filters could lead to token pollution. And some headers are not relevant for
    classification and can be safely ignored to reduce token count.
    """


class EmailParser(Parser):
    """
    A parser for email messages that extracts the email body and metadata such as sender, recipient, subject, and date.

    The email body and metadata are decoded into plain text, removing UTF-8 encoding and any email-specific formatting.
    The metadata is returned as a dictionary with keys corresponding to the email headers.
    """

    API_VERSION: str = "1.0"

    STRIP_HTML_REGEX = re.compile(r"<[^>]+>")

    settings: EmailParserSettings

    async def __call__(self, fp: AsyncFile[str]) -> ParseResult:
        file_content = await fp.read()
        message_parser = PyEmailParser(policy=email.policy.default, _class=EmailMessage)
        try:
            message = cast(EmailMessage, message_parser.parsestr(file_content))  # type: ignore[redundant-cast]
        except TypeError:
            raise DspamParseError("Failed to parse email")

        content = self.parse_body(message)
        metadata = self.parse_headers(message)
        return ParseResult(content, metadata)

    def parse_body(self, message: EmailMessage) -> str:
        """Extract the decoded text/plain body without message headers."""
        if message.is_multipart():
            # TODO: look into multipart/related
            body_part = message.get_body(preferencelist=("html", "plain"))
            if body_part is None:
                raise DspamParseError("Email does not contain a supported body part")

            if body_part.get_content_type() == "text/html":
                content = self.parse_html_body(body_part)
            elif body_part.get_content_type() == "text/plain":
                content = body_part.get_content()
            else:
                raise DspamParseError(
                    "Unsupported email body content type: {}".format(
                        body_part.get_content_type()
                    )
                )
        else:
            if message.get_content_type() == "text/html":
                content = self.parse_html_body(message)
            elif message.get_content_type() == "text/plain":
                content = message.get_content()
            else:
                raise DspamParseError(
                    "Unsupported email body content type: {}".format(
                        message.get_content_type()
                    )
                )

        if not isinstance(content, str):
            raise DspamParseError("Failed to decode email body as text")

        return content

    def parse_headers(self, message: EmailMessage) -> Metadata:
        """Extract metadata from email headers"""
        ignore_headers = [h.lower() for h in self.settings.ignore_headers]

        headers = {}
        for header_name in message.keys():
            if header_name.lower() in ignore_headers:
                logger.debug(f"Ignoring header: {header_name}")
                continue
            header_value = message.get_all(header_name)
            if header_value is None:
                continue
            if len(header_value) == 1:
                headers[header_name] = header_value[0]
            else:
                headers[header_name] = header_value
        return headers

    def parse_html_body(self, message_part: MIMEPart) -> str:
        """Extract text content from an HTML email body."""
        html_content = message_part.get_content()
        # Simple way to extract text from HTML: remove tags for decode entities.
        # For a more robust solution, consider using an HTML parser like BeautifulSoup.
        text_content = re.sub(self.STRIP_HTML_REGEX, "", html_content)
        text_content = html.unescape(text_content)
        return text_content.strip()
