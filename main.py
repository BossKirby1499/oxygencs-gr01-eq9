class App:
    def __init__(self):
        self._hub_connection = None
        self.TICKS = 10

        # To be configured by your team
        self.HOST = None  # Setup your host here
        self.TOKEN = None  # Setup your token here
        self.T_MAX = None  # Setup your max temperature here
        self.T_MIN = None  # Setup your min temperature here
        self.DATABASE_URL = None  # Setup your database here