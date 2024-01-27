import itertools

from .doc_handler import DocHandler
from .foss import LibreHandler, GmailSender
from .ms import WordHandler, OutlookSender
from .system_tools import (
    check_word,
    check_excel,
    check_libre,
    check_outlook,
    check_lib2,
)
from .email_handler import EmailHandler


class OfficeTools:
    def __init__(self, doc: DocHandler, email: EmailHandler):
        self.doc: DocHandler = doc
        self.email: EmailHandler = email

    @classmethod
    def microsoft(cls) -> 'OfficeTools':
        try:
            return cls(WordHandler(), OutlookSender())
        except OSError:
            raise OSError('Microsoft Office tools are not installed')

    @classmethod
    def libre(cls) -> 'OfficeTools':
        try:
            return cls(LibreHandler(), GmailSender())
        except OSError:
            raise OSError('LibreOffice tools are not installed')

    @classmethod
    def auto_select(cls) -> 'OfficeTools':
        if not tools_available():
            raise OSError('Neither Microsoft nor LibreOffice tools are installed')

        doc_handler = WordHandler if check_word() else LibreHandler
        email_handler = OutlookSender if check_outlook() else GmailSender

        return cls(doc_handler(), email_handler())


def tools_available() -> bool:
    """Check if either Microsoft or LibreOffice tools
    for docs and sheets are installed"""
    libre = check_libre()
    word = check_word()
    excel = check_excel()
    return all([(word or libre), (excel or libre)])


def get_installed_combinations():
    doc_handlers = []
    email_handlers = []

    if check_word():
        doc_handlers.append(WordHandler)
    if check_lib2():
        doc_handlers.append(LibreHandler)

    if check_outlook():
        email_handlers.append(OutlookSender)

    email_handlers.append(GmailSender)

    for doc_handler, email_handler in itertools.product(doc_handlers, email_handlers):
        yield OfficeTools(doc_handler(), email_handler())
