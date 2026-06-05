import email
import email.policy
from email.parser import Parser as PyEmailParser
from email.message import EmailMessage as PyEmailMessage

from anyio import AsyncFile

from dspam.exceptions import DspamParseError
from dspam.parse import Parser, ParseResult


class EmailParser(Parser):
    """
    A parser for email messages that extracts the email body and metadata such as sender, recipient, subject, and date.

    The email body and metadata are decoded into plain text, removing UTF-8 encoding and any email-specific formatting.
    The metadata is returned as a dictionary with keys corresponding to the email headers.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, fp: AsyncFile) -> ParseResult:
        # Bridge async AsyncFile to sync email.message_from_file
        file_content = await fp.read()
        if isinstance(file_content, bytes):
            file_content = file_content.decode("utf-8")

        message_parser = PyEmailParser(
            policy=email.policy.default, _class=PyEmailMessage
        )
        message: PyEmailMessage = message_parser.parsestr(file_content)
        if message is None:
            raise DspamParseError("Failed to parse email")
        # For now, assume the message has no mime-encoded parts and is a simple text email
        # Note: this also returns message headers :(
        content = message.get_body(preferencelist=("plain", "html")).as_string()  # type: ignore[union-attr]

        # For now, ignore that messages can have multiple headers with the same name (e.g. Received)
        metadata = {k: v for k, v in message.items()}
        return ParseResult(content, metadata)
