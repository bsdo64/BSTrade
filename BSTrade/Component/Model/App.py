from enum import Enum, auto


class Provider(Enum):
    BITMEX = auto()
    UPBIT = auto()
    COINONE = auto()
    BINANCE = auto()


class AppModel:
    def __init__(self):
        self.exchanges = Provider
        self.selected_exchange = Provider(1)
