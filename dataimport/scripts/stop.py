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
        previous_trial_start = None

        max_round = 0
        round_trial_counts = {}

        sheet.cell(
            column=1, row=1, value='Data ({}) from {}'.format(
                self.all_data_file_idx,
                self.filename)
        )

        for idx, col_header in enumerate(col_headers):
            sheet.cell(column=idx+1, row=2, value=col_header)

        # Rows within a session
        for s_idx, trial in enumerate(session_data):

            # print('row', s_idx)

            for col_idx, col_header in enumerate(col_headers):
                value = trial[col_header]

                if col_header == 'tapResponseStart' and value:
                    response_times.append(value)

                sheet.cell(column=col_idx+1, row=s_idx+3, value=value)

            # roundID
            if 'roundID' in trial and trial['roundID']:
                if trial['roundID'] > max_round:
                    max_round = trial['roundID']

                if trial['roundID'] in round_trial_counts:
                    round_trial_counts[trial['roundID']] = round_trial_counts[trial['roundID']] + 1
                else:
                    round_trial_counts[trial['roundID']] = 0

            # Trial duration: trialEnd - trialStart
            if 'trialEnd' in trial and 'trialStart' in trial:
                if trial['trialEnd'] and trial['trialStart']:
                    trial_duration = trial['trialEnd'] - trial['trialStart']
                    sheet.cell(column=len(col_headers) + 1, row=2, value="Trial Duration")
                    sheet.cell(column=len(col_headers) + 1, row=s_idx+3, value=trial_duration)

            # Stop signal duration: stopSignalOffset - stopSignalOnset
            if 'stopSignalOffset' in trial and 'stopSignalOnset' in trial:
                if trial['stopSignalOffset'] and trial['stopSignalOnset']:
                    stop_signal_duration = trial['stopSignalOffset'] - trial['stopSignalOnset']
                    sheet.cell(column=len(col_headers) + 2, row=2, value="Stop Signal Duration")
                    sheet.cell(column=len(col_headers) + 2, row=s_idx+3, value=stop_signal_duration)

            # Stimulus duration: stimulusOffset - stimulusOnset
            if 'stimulusOffset' in trial and 'stimulusOnset' in trial:
                stimulus_duration = trial['stimulusOffset'] - trial['stimulusOnset']
                sheet.cell(column=len(col_headers) + 3, row=2, value="Stimulus Duration")
                sheet.cell(column=len(col_headers) + 3, row=s_idx+3, value=stimulus_duration)

            # Difference between signal onset and stop signal delay: stopSignalOnset - stopSignalDelay
            if 'stopSignalOnset' in trial and 'stopSignalDelay' in trial:
                if trial['stopSignalOnset'] and trial['stopSignalDelay']:
                    signal_stop_delay = trial['stopSignalOnset'] - trial['stopSignalDelay']
                    sheet.cell(column=len(col_headers) + 4, row=2, value="stopSignalOnset - stopSignalDelay")
                    sheet.cell(column=len(col_headers) + 4, row=s_idx + 3, value=signal_stop_delay)

            # interTrialInterval
            # Duration between trials: trialOnsetB - trialOnsetA,
            # where B is the trial of interest and A is the trial preceding that.
            # Calculations needed without 1st trial of each block (because of inter-block/graphical feedback).
            # TODO does 'trialOnsetA' mean trialStart?
            if 'trialStart' in trial:
                if trial['trialStart']:
                    if previous_trial_start:
                        interTrialInterval = trial['trialStart'] - previous_trial_start
                        sheet.cell(column=len(col_headers) + 5, row=2,
                                   value="interTrialInterval")
                        sheet.cell(column=len(col_headers) + 5, row=s_idx + 3,
                                   value=interTrialInterval)
                    previous_trial_start = trial['trialStart']

            # Duration between signal offset and stimulus offset: stimulusOffset - stopSignalOffset
            if 'stimulusOffset' in trial and 'stopSignalOffset' in trial:
                if trial['stimulusOffset'] and trial['stopSignalOffset']:
                    # TODO this is zero apparently
                    signal_stimulus_offsets = trial['stimulusOffset'] - trial['stopSignalOffset']
                    sheet.cell(column=len(col_headers) + 6, row=2, value="stimulusOffset - stopSignalOffset")
                    sheet.cell(column=len(col_headers) + 6, row=s_idx + 3, value=signal_stimulus_offsets)

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

            sheet2.cell(column=5, row=2, value='Session Event Count')
            sheet2.cell(column=5, row=3, value=len(session_data))

            sheet2.cell(column=6, row=2, value='Max round ID')
            sheet2.cell(column=6, row=3, value=max_round)

            # round number and count
            sheet2.cell(column=7, row=2, value='Round trial numbers')
            sheet2.cell(column=8, row=2, value='Round trial count')
            for itr, value in enumerate(round_trial_counts):
                sheet2.cell(column=7, row=3 + itr, value=value)
                sheet2.cell(column=8, row=3 + itr, value=round_trial_counts[value])


        except Exception as e1:
            print(e1)

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
            task_count = 0
            for idx, a in enumerate(all_data):

                print((idx + 1), a['type'])

                self.all_data_file_idx = idx

                all_types.append(a['type'])
                if 'data' in a:
                    if isinstance(a['data'], list) and len(a['data']):
                        print(a['data'])
                        if 'sessionEvents' in a['data'][0]:
                            task_count += len(a['data'][0]['sessionEvents'])

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
            print('task_count', task_count)


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
