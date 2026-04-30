from dspam.parse import BaseParser
import email


class EmailParser(BaseParser):
    """
    A parser for email messages that extracts the email body and metadata such as sender, recipient, subject, and date.

    The email body and metadata are decoded into plain text, removing UTF-8 encoding and any email-specific formatting. The metadata is returned as a dictionary with keys corresponding to the email headers.
    """

    async def __call__(self, *args, **kwargs) -> tuple[str, dict[str, str]]:
        message = email.message_from_file(self.fp)
        # assume the message has no mime-encoded parts and is a simple text email
        content = message.get_payload(decode=True)
        metadata = {
            "From": message.get("From", ""),
            "To": message.get("To", ""),
            "Subject": message.get("Subject", ""),
            "Date": message.get("Date", ""),
        }
        return content, metadata
