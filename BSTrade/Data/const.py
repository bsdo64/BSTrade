from enum import Enum, auto


class Provider(Enum):
    BITMEX = auto()
    UPBIT = auto()
    COINONE = auto()


class HttpEndPointType(Enum):
    exchange_status = auto()
    candles = auto()
    symbols = auto()
    orderbook = auto()
    ticker = auto()


def find_enum(item: str, enum: Enum):
    item_up = item.upper()
    found = None
    for name, mem in enum.__members__.items():
        if name == item_up:
            found = mem

    return found
