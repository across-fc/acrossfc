# stdlib
from io import StringIO
from typing import Optional


class Report:
    """
    Encapsulates the formatting and publishing logic of a report.
    """
    def __init__(self,
                 emoji: Optional[str],
                 title: str,
                 header: Optional[str],
                 data: str,
                 footer: Optional[str]):
        self.emoji = emoji
        self.title = title
        self.header = header
        self.data = data
        self.footer = footer

    def to_cli_str(self) -> str:
        buffer = StringIO()

        buffer.write('\n')
        buffer.write(self.title)

        if self.header is not None:
            buffer.write('\n\n')
            buffer.write(self.header)

        buffer.write('\n\n')
        buffer.write(self.data)

        if self.footer is not None:
            buffer.write('\n\n')
            buffer.write(self.footer)

        return buffer.getvalue()

    def to_discord_str(self) -> str:
        buffer = StringIO()

        if self.emoji is not None:
            buffer.write(self.emoji)
            buffer.write(' ')
        buffer.write('**')
        buffer.write(self.title)
        buffer.write('**')

        if self.header is not None:
            buffer.write('\n\n')
            buffer.write(self.header)

        buffer.write('\n```\n')
        buffer.write(self.data)
        buffer.write('```')

        if self.footer is not None:
            buffer.write('\n\n')
            buffer.write(self.footer)

        return buffer.getvalue()
