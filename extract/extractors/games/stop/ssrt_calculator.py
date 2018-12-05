from .abstract_stop_evaluator import AbstractStopEvaluator

from utils import get_session_events, numericify, remove_none_values


class SSRTCalculator(AbstractStopEvaluator):

    def __init__(self):
        self.mean_ideal_ssrt = None
        self.mean_actual_ssrt = None
        self.ideal_integration_ssrt = None
        self.actual_integration_ssrt = None
        self.mean_stop_signal_delay = None
        self.mean_stop_signal_onset = None

    def evaluate(self, row):
        self.calculate_ssrt(row)

    def calculate_ssrt(self, row):
        session_events = get_session_events(row)
        self.calculate_mean_ssrt(session_events)
        self.calculate_integration_ssrt(session_events)

    def calculate_mean_ssrt(self, session_events):
        tap_response_start_total = 0
        stop_signal_delay_total = 0
        stop_signal_onset_total = 0
        for session_event in session_events:
            trial_type = session_event['trialType']
            tap_response_start = numericify(session_event['tapResponseStart'])
            if trial_type == 'GO' and tap_response_start > 0:
                tap_response_start_total += tap_response_start
            stop_signal_delay = numericify(session_event['stopSignalDelay'])
            stop_signal_delay_total += stop_signal_delay
            stop_signal_onset = numericify(session_event['stopSignalOnset'])
            stop_signal_onset_total += stop_signal_onset
        mean_tap_response_start = tap_response_start_total / len(session_events)
        self.mean_stop_signal_delay = stop_signal_delay_total / len(session_events)
        self.mean_stop_signal_onset = stop_signal_onset_total / len(session_events)
        self.mean_ideal_ssrt = mean_tap_response_start - self.mean_stop_signal_delay  # What the SSRT should be
        self.mean_actual_ssrt = mean_tap_response_start - self.mean_stop_signal_onset  # What the SSRT actually is
        # print('\n IDEAL MEAN SSRT:', self.mean_ideal_ssrt)
        # print('ACTUAL MEAN SSRT:', self.mean_actual_ssrt)

    def calculate_integration_ssrt(self, session_events):
        go_trial_count = 0
        stop_trial_count = 0
        stop_trail_with_response_count = 0
        incorrect_stop_trials_count = 0
        go_trial_tap_response_starts = []
        for session_event in session_events:
            trial_type = session_event['trialType']
            tap_response_start = session_event['tapResponseStart']
            if trial_type == 'GO':
                go_trial_count += 1
                go_trial_tap_response_starts.append(tap_response_start)
            elif trial_type == 'STOP':
                stop_trial_count += 1
                if tap_response_start:
                    stop_trail_with_response_count += 1
            tap_response_type = session_event['tapResponseType']
            if tap_response_type in ['INCORRECT_STOP', 'MISS_STOP']:
                incorrect_stop_trials_count += 1
        go_trial_tap_response_starts = remove_none_values(go_trial_tap_response_starts)
        go_trial_tap_response_starts.sort()
        stop_signal_trial_probability = stop_trail_with_response_count / stop_trial_count
        n = go_trial_count * stop_signal_trial_probability
        # print('GO TRIALS TRSs:', go_trial_tap_response_starts)
        # print('GO TRIALS TRSs count:', len(go_trial_tap_response_starts))
        # print('INCORRECT STOP TRIALS:', incorrect_stop_trials_count)
        # print('p(stop signal trial):', stop_signal_trial_probability)
        # print('n:', n)
        n = int(n) - 1
        assert n >= 0
        nth = go_trial_tap_response_starts[int(n)]
        # print('nth:', nth)
        self.ideal_integration_ssrt = nth - self.mean_stop_signal_delay
        self.actual_integration_ssrt = nth - self.mean_stop_signal_onset
        # print('ideal_integration_ssrt:', self.ideal_integration_ssrt)
        # print('actual_integration_ssrt:', self.actual_integration_ssrt)

    def populate_spreadsheet(self, spreadsheet):
        spreadsheet.select_sheet('SSRT')

        spreadsheet.set_values(['Ideal Mean SSRT', self.mean_ideal_ssrt])
        spreadsheet.set_values(['Actual Mean SSRT', self.mean_actual_ssrt])

        spreadsheet.set_values(['Ideal Integration SSRT', self.ideal_integration_ssrt])
        spreadsheet.set_values(['Actual Integration SSRT', self.actual_integration_ssrt])
