import csv
import json

import os
from pathlib import Path
from settings import food_control_path
from extractors import ExtractorFactory
from keypathdict import KeypathDict


class Extractor:

    extractor_factory = ExtractorFactory()

    def extract_from_json_filename(self, json_filename, json_csv_path):
        with open(json_filename, 'r', encoding='utf-8') as json_file:
            json_array = json.load(json_file)
        self.extract_from_json(json_array, json_csv_path)

    def extract_from_json(self, json_array, json_csv_path):
        for extractor in self.extractor_factory.extractors:
            print('\nEXTRACTOR: {}'.format(extractor.type))
            self.extract_row_type(json_array, extractor, json_csv_path)

    def extract_row_type(self, json_array, extractor, json_csv_path):
        if not self.has_row_to_extract(json_array, extractor):
            print('no rows to extract with: ', extractor.type)
            return

        output_filename = json_csv_path / '{}.csv'.format(extractor.type)
        with open(output_filename, 'w', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow(extractor.column_names())
            for row in json_array:
                row = KeypathDict(row)
                if extractor.process(row):
                    print(extractor.row_values())
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
        '060618.json',
        '070618.json',
    ]


    def create_folder(path):
        path.mkdir(parents=True, exist_ok=True)

    def filename_without_extension(filename):
        (base_filename, _) = os.path.splitext(os.path.basename(json_filename))
        return base_filename


    csv_path = Path('./csv')
    create_folder(csv_path)
    for json_filename in json_filenames:
        json_csv_path = csv_path / filename_without_extension(json_filename)
        create_folder(json_csv_path)
        filename = food_control_path / json_filename
        extractor.extract_from_json_filename(filename, json_csv_path)
