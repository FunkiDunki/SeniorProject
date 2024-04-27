import dataclasses as dc


@dc.dataclass
class CustomError(Exception):
    """
    this class allows you to raise custom exceptions
    """

    message: str
