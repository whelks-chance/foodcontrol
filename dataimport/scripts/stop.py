import json

import os
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

    def output_srgame_spreadsheet(self, json_blob, folder='test_folder', output_filepath='test101.xlsx'):
        # extra_headers = [{
        #     'col': 'tapResponseStart',
        #     'output': 'avg_response',
        #     'method': 'avg'
        # }]

        session_data = json_blob['data'][0]['sessionEvents']
        col_headers = sorted(session_data[0].keys())

        wb = Workbook()
        # wb.sheetnames
        sheet = wb.active
        sheet.title = 'Data Output'

        response_times = []
        session_start = json_blob['data'][0]['sessionStart']
        session_end = json_blob['data'][0]['sessionEnd']

        sheet.cell(
            column=1, row=1, value='Data ({}) from {}'.format(
                self.all_data_file_idx,
                self.filename)
        )

        for idx, col_header in enumerate(col_headers):
            sheet.cell(column=idx+1, row=2, value=col_header)

        for s_idx, trial in enumerate(session_data):

            print('row', s_idx)

            trial_start = None
            trial_end = None

            stop_signal_offset = None
            stop_signal_onset = None

            for col_idx, col_header in enumerate(col_headers):
                value = trial[col_header]

                if col_header == 'trialStart' and value:
                    trial_start = value
                if col_header == 'trialEnd' and value:
                    trial_end = value

                if col_header == 'stopSignalOffset' and value:
                    stop_signal_offset = value
                if col_header == 'stopSignalOnset' and value:
                    stop_signal_onset = value

                if col_header == 'tapResponseStart' and value:
                    response_times.append(value)

                sheet.cell(column=col_idx+1, row=s_idx+3, value=value)

            if trial_start and trial_end:
                trial_duration = trial_end - trial_start
                sheet.cell(column=len(col_headers) + 1, row=2, value="trialDuration")
                sheet.cell(column=len(col_headers) + 1, row=s_idx+3, value=trial_duration)

            if stop_signal_offset and stop_signal_onset:
                stop_signal_duration = stop_signal_offset - stop_signal_onset
                sheet.cell(column=len(col_headers) + 2, row=2, value="stopSignalDuration")
                sheet.cell(column=len(col_headers) + 2, row=s_idx+3, value=stop_signal_duration)



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

            sheet2.cell(column=4, row=2, value='Session Duration')
            sheet2.cell(column=4, row=3, value=(session_end - session_start))
        except:
            pass

        parent = os.path.dirname(os.path.abspath(output_filepath))
        new_folder = os.path.join(parent, folder)
        if not os.path.exists(new_folder):
            os.mkdir(new_folder)

        output_file_and_dir = os.path.join(new_folder, output_filepath)
        print(output_file_and_dir)
        wb.save(output_file_and_dir)

    def sort_all_data(self, all_data_file):
        self.filename = all_data_file

        head, tail = os.path.split(self.filename)
        new_folder_name = tail.split('.')[0]

        with open(all_data_file, 'r') as all_data_handle:
            all_data =  json.load(all_data_handle)

            all_types = []
            for idx, a in enumerate(all_data):

                print((idx + 1), a['type'])

                self.all_data_file_idx = idx

                all_types.append(a['type'])

                if a['type'] == 'STOP':
                    self.output_srgame_spreadsheet(
                        a,
                        folder=new_folder_name,
                        output_filepath='{}_STOP_{}.xlsx'.format(
                            a['userId'],
                            a['data'][0]['gameSessionID']
                        )
                    )

                if a['type'] == 'NASTOP':
                    self.output_srgame_spreadsheet(
                        a,
                        folder=new_folder_name,
                        output_filepath='{}_NASTOP_{}.xlsx'.format(
                            a['userId'],
                            a['data'][0]['gameSessionID']
                        )
                    )

                if a['type'] == 'GSTOP':
                    self.output_srgame_spreadsheet(
                        a,
                        folder=new_folder_name,
                        output_filepath='{}_GSTOP_{}.xlsx'.format(
                            a['userId'],
                            a['data'][0]['gameSessionID']
                        )
                    )

                if a['type'] == 'GRESTRAINT':
                    self.output_srgame_spreadsheet(
                        a,
                        folder=new_folder_name,
                        output_filepath='{}_GRESTRAINT_{}.xlsx'.format(
                            a['userId'],
                            a['data'][0]['gameSessionID']
                        )
                    )

                if a['type'] == 'DOUBLE':
                    self.output_srgame_spreadsheet(
                        a,
                        folder=new_folder_name,
                        output_filepath='{}_DOUBLE_{}.xlsx'.format(
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

    data_dir = '../../'
    abspath = os.path.abspath(data_dir)
    # all_data_file = '200318_new.json'
    # rs.sort_all_data(os.path.join(data_dir, all_data_file))

    all_data_file = '020518.json'
    rs.sort_all_data(os.path.join(data_dir, all_data_file))
