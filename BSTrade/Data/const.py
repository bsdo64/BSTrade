from enum import Enum, auto


class Provider(Enum):
    BITMEX = auto()
    UPBIT = auto()
    COINONE = auto()


class HttpEndPointType(Enum):
    get_exchange_status = auto()
    get_candles = auto()
    get_symbols = auto()
    get_orderbook = auto()
    get_ticker = auto()


def find_enum(item: str, enum: Enum):
    item_up = item.upper()
    found = None
    for name, mem in enum.__members__.items():
        if name == item_up:
            found = mem

    return found
