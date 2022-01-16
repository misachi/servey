class Server:
    WORKERS = {}
    def __init__(self, config) -> None:
        self.cfg = config