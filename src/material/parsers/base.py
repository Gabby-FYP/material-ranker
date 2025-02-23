import abc


class BasePDFParser(abc.ABC):

    def __init__(self, file: bytes):
        self.file = file

    @abc.abstractmethod
    def parse(self) -> str:
        """Parse the given file and exract text content."""
