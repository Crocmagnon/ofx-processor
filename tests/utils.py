import datetime
from dataclasses import dataclass


@dataclass
class OfxTransaction:
    """
    Mimick what is retrieved via ofxtools when parsing the file
    """

    name: str = ""
    memo: str = ""
    dtposted: datetime.datetime = None
    trnamt: float = 0
    trntype: str = ""
