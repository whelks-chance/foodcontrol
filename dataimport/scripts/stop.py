import json

from openpyxl.workbook import Workbook
from openpyxl.reader.excel import load_workbook, InvalidFileException
from openpyxl.cell import Cell


class ReadStop:

    def output_spreadsheet(self, json_file):
        extra_headers = [{
            'col': 'tapResponseStart',
            'output': 'avg_response',
            'method': 'avg'
        }]

        with open(json_file, 'r') as json_file_handle:
            json_blob = json.load(json_file_handle)

            session_data = json_blob[0]['data'][0]['sessionEvents']

            print(len(session_data))

            col_headers = sorted(session_data[0].keys())
            print(col_headers)

            # for trial in session_data:
            #     print(trial.keys())

            wb = Workbook()
            wb.get_sheet_names()
            sheet = wb.active
            sheet.title = 'Data Output'

            filepath = "test101.xlsx"

            response_times = []

            for idx, col_header in enumerate(col_headers):
                sheet.cell(column=idx+1, row=1, value=col_header)

            for s_idx, trial in enumerate(session_data):
                for col_idx, col_header in enumerate(col_headers):
                    value = trial[col_header]

                    if col_header == 'tapResponseStart' and value:
                        response_times.append(value)

                    sheet.cell(column=col_idx+1, row=s_idx+2, value=value)

            response_times = sorted(response_times)
            avg_res = sum(response_times) / len(response_times)

            wb.create_sheet('Data Summary')
            sheet2 = wb['Data Summary']
            sheet2.cell(column=1, row=1, value='Response Avg')
            sheet2.cell(column=1, row=2, value=avg_res)

            sheet2.cell(column=2, row=1, value='Response Low')
            sheet2.cell(column=2, row=2, value=response_times[0])

            sheet2.cell(column=3, row=1, value='Response High')
            sheet2.cell(column=3, row=2, value=response_times[-1])

            wb.save(filepath)


if __name__ == '__main__':
    rs = ReadStop()

    json_file = '/home/ianh/Downloads/STOP.json'
    rs.output_spreadsheet(json_file)