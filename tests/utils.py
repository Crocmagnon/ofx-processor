import datetime


class OfxTransaction:
    """
    Mimick what is retrieved via ofxtools when parsing the file
    """

    def __init__(
        self,
        name: str = "",
        memo: str = "",
        dtposted: datetime.datetime = None,
        trnamt: float = 0,
    ):
        self.dtposted = dtposted
        self.memo = memo
        self.trnamt = trnamt
        self.name = name
