import csv
import json

from pathlib import Path
from settings import food_control_path
from extractors import ExtractorFactory


class Extractor:

    extractor_factory = ExtractorFactory()

    def extract_from_json_filename(self, json_filename):
        with open(json_filename, 'r', encoding='utf-8') as json_file:
            json_array = json.load(json_file)
        self.extract_from_json(json_array)

    def extract_from_json(self, json_array):
        for extractor in self.extractor_factory.extractors:
            print('\n{}'.format(extractor.type))
            self.extract_row_type(json_array, extractor)

    def extract_row_type(self, json_array, extractor):
        if not self.has_row_to_extract(json_array, extractor):
            return

        output_filename = 'csv/{}.csv'.format(extractor.type)
        with open(output_filename, 'w', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow(extractor.column_names())
            for row in json_array:
                if extractor.process(row):
                    csv_writer.writerow(extractor.row_values())

    @staticmethod
    def has_row_to_extract(json_array, extractor):
        for row in json_array:
            if extractor.can_process_row(row):
                return True
        return False


if __name__ == '__main__':
    extractor = Extractor()

    json_filenames = [
        # '020518.json', #  Old format?
        # '060618.json',
        '070618.json',
    ]


    def create_folder(path):
        path.mkdir(parents=True, exist_ok=True)


    csv_path = Path('./csv')
    create_folder(csv_path)
    for json_filename in json_filenames:
        filename = food_control_path / json_filename
        print(filename)
        extractor.extract_from_json_filename(filename)
