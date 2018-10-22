import os
import csv
import json

from settings import JSON_PATH, CSV_PATH
from extractors import ExtractorFactory


class Extractor:

    extractor_factory = ExtractorFactory()

    def extract_from_json(self, json_array, json_csv_path):
        for extractor in self.extractor_factory.extractors:
            print('\nEXTRACTOR: {}'.format(extractor.type))
            self.extract_row_type(json_array, extractor, json_csv_path)

    def extract_row_type(self, json_array, extractor, json_csv_path):
        if not self.has_row_to_extract(json_array, extractor):
            print('no rows to extract with: ', extractor.type)
            return

        csv_filename = extractor.get_filename()
        if csv_filename.endswith('-'):
            csv_filename = csv_filename[:-1]
        output_filename = json_csv_path / '{}.csv'.format(csv_filename.upper())
        with open(output_filename, 'w', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')
            for row in json_array:
                if extractor.process_row(row):
                    for extracted_row in extractor.extracted_rows():
                        csv_writer.writerow(extracted_row)

        # We need to prepend the column header row to the file containing the data rows
        # because in the case of question extraction the column names are not known until
        # a row has been read
        with open(output_filename, 'r+', encoding='utf-8') as csv_file:
            file_data = csv_file.read()  # Read the data rows
            csv_file.seek(0, 0)          # Move the file pointer to the beginning
            csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')
            column_names = extractor.get_column_names()
            csv_writer.writerow(column_names)  # Write the header row
            csv_file.write(file_data)          # Write the data rows

    @staticmethod
    def has_row_to_extract(json_array, extractor):
        for row in json_array:
            # print(row)
            if extractor.can_process_row(row):
                # print(row)
                return True
        return False


if __name__ == '__main__':
    extractor = Extractor()

    json_filenames = [
        # '020518.json',
        # '060618.json',
        # '070618.json',
        # '200818.json',
        # '040918.json',
        # '260918.json',
        '010618_to_040918.json',
    ]

    def create_folder(path):
        path.mkdir(parents=True, exist_ok=True)

    def filename_without_extension(filename):
        base_filename, _ = os.path.splitext(os.path.basename(json_filename))
        return base_filename

    create_folder(CSV_PATH)
    for json_filename in json_filenames:
        json_path = JSON_PATH / json_filename
        with open(json_path, 'r', encoding='utf-8') as json_file:
            json_array = json.load(json_file)
        user_id = json_array[0]['userId'].lower()
        session_id = json_array[0]['sessionId']
        json_csv_path = CSV_PATH / '{}-{}-{}'.format(filename_without_extension(json_filename), user_id, session_id)
        create_folder(json_csv_path)
        extractor.extract_from_json(json_array, json_csv_path)
