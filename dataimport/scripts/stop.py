import json

from openpyxl.workbook import Workbook
from openpyxl.reader.excel import load_workbook, InvalidFileException
from openpyxl.cell import Cell


class ReadStop:

    def __init__(self):
        self.filename = ''
        self.all_data_file_idx = 0

    def read_stop_file(self, json_file):
        with open(json_file, 'r') as json_file_handle:
            json_blob = json.load(json_file_handle)
            self.output_srgame_spreadsheet(json_blob[0])

    def output_srgame_spreadsheet(self, json_blob, output_filepath='test101.xlsx'):
        # extra_headers = [{
        #     'col': 'tapResponseStart',
        #     'output': 'avg_response',
        #     'method': 'avg'
        # }]

        session_data = json_blob['data'][0]['sessionEvents']
        col_headers = sorted(session_data[0].keys())

        wb = Workbook()
        wb.get_sheet_names()
        sheet = wb.active
        sheet.title = 'Data Output'

        response_times = []

        sheet.cell(
            column=1, row=1, value='Data ({}) from {}'.format(
                self.all_data_file_idx,
                self.filename)
        )

        for idx, col_header in enumerate(col_headers):
            sheet.cell(column=idx+1, row=2, value=col_header)

        for s_idx, trial in enumerate(session_data):
            for col_idx, col_header in enumerate(col_headers):
                value = trial[col_header]

                if col_header == 'tapResponseStart' and value:
                    response_times.append(value)

                sheet.cell(column=col_idx+1, row=s_idx+3, value=value)

        try:
            response_times = sorted(response_times)
            avg_res = sum(response_times) / len(response_times)

            wb.create_sheet('Data Summary')
            sheet2 = wb['Data Summary']
            sheet2.cell(column=1, row=2, value='Response Avg')
            sheet2.cell(column=1, row=3, value=avg_res)

            sheet2.cell(column=2, row=2, value='Response Low')
            sheet2.cell(column=2, row=3, value=response_times[0])

            sheet2.cell(column=3, row=2, value='Response High')
            sheet2.cell(column=3, row=3, value=response_times[-1])
        except:
            pass

        wb.save(output_filepath)

    def sort_all_data(self, all_data_file):
        self.filename = all_data_file

        with open(all_data_file, 'r') as all_data_handle:
            all_data =  json.load(all_data_handle)

            all_types = []
            for idx, a in enumerate(all_data):
                self.all_data_file_idx = idx

                all_types.append(a['type'])

                if a['type'] == 'STOP':
                    self.output_srgame_spreadsheet(
                        a, output_filepath='{}_STOP_{}.xlsx'.format(
                            a['userId'],
                            a['data'][0]['gameSessionID']
                        )
                    )

                if a['type'] == 'NASTOP':
                    self.output_srgame_spreadsheet(
                        a, output_filepath='{}_NASTOP_{}.xlsx'.format(
                            a['userId'],
                            a['data'][0]['gameSessionID']
                        )
                    )

                if a['type'] == 'GSTOP':
                    self.output_srgame_spreadsheet(
                        a, output_filepath='{}_GSTOP_{}.xlsx'.format(
                            a['userId'],
                            a['data'][0]['gameSessionID']
                        )
                    )

                if a['type'] == 'GRESTRAINT':
                    self.output_srgame_spreadsheet(
                        a, output_filepath='{}_GRESTRAINT_{}.xlsx'.format(
                            a['userId'],
                            a['data'][0]['gameSessionID']
                        )
                    )

                if a['type'] == 'DOUBLE':
                    self.output_srgame_spreadsheet(
                        a, output_filepath='{}_DOUBLE_{}.xlsx'.format(
                            a['userId'],
                            a['data'][0]['gameSessionID']
                        )
                    )

                if a['type'] == 'virtual-supermarket-selected':
                    print('virtual-supermarket-selected idx', idx)

            print(set(all_types))


if __name__ == '__main__':
    rs = ReadStop()

    # json_file = '/home/ianh/Downloads/STOP.json'
    # rs.read_stop_file(json_file)

    all_data_file = '/home/ianh/Downloads/200318_new.json'
    rs.sort_all_data(all_data_file)