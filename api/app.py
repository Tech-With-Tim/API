from quart import Quart


class API(Quart):
    """Quart subclass to implement more API like handling."""
    pass


app = API(__name__)
