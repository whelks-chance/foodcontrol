from ..dataextractor import DataExtractor


class GameDataExtractor(DataExtractor):
    """The abstract base class for all game data extractors"""

    def __init__(self):
        super().__init__()
        self.values = {}

    def extract_row_data(self, row):
        print(row['data'])
        self.values = self.extract_values(row)
        self.check(row)
        self.calculate(row)

    def check(self, row):
        """Override to perform extractor-specific row checks"""
        pass

    def calculate(self, row):
        """Override to perform extractor-specific row calculations"""
        pass

    def extracted_rows(self):
        return [self.listify_values(self.get_column_names(), self.values)]
