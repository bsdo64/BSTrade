

class ExchangeModel:
    def __init__(self, provider):
        self._provider = provider
        self._name: str = provider.name
        self._symbols: list = []

    @property
    def provider(self):
        return self._provider

    @property
    def name(self) -> str:
        return self._name

    @property
    def symbols(self) -> list:
        return self._symbols

    @symbols.setter
    def symbols(self, syms):
        self._symbols = syms
