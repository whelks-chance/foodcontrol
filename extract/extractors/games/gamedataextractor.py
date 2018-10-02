from ..dataextractor import DataExtractor


class GameDataExtractor(DataExtractor):
    """The abstract base class for all game data extractors"""

    def __init__(self):
        super().__init__()
        self.csv_rows = []

    def extract_row_data(self, row):
        self.csv_rows = self.extract_values(row)
        self.check(row)
        self.calculate(row)

    def check(self, row):
        """Override to perform extractor-specific row checks"""
        pass

    def calculate(self, row):
        """Override to perform extractor-specific row calculations"""
        pass
