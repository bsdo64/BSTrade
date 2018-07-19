import pandas as pd


class Manager:
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        self.series = data
        data_length = len(data)
        self.range = data_length if data_length < 100 else 100
        self.marker_gap = 30
