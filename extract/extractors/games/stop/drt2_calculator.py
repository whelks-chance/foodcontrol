import statistics

from .abstract_stop_evaluator import AbstractStopEvaluator

from utils import get_session_events, numericify


class DRT2Calculator(AbstractStopEvaluator):

    def __init__(self):
        self.ideal_drt2_stats = None
        self.actual_drt2_stats = None

    def evaluate(self, row):
        session_events = get_session_events(row)
        ideal_drt2s = []
        actual_drt2s = []
        for session_event in session_events:
            second_tap_response_start = numericify(session_event['secondTapResponseStart'])
            # Ideal DRT2
            stop_signal_delay = numericify(session_event['stopSignalDelay'])
            ideal_drt2 = second_tap_response_start - stop_signal_delay
            ideal_drt2s.append(ideal_drt2)
            # Actual DRT2
            stop_signal_onset = numericify(session_event['stopSignalOnset'])
            actual_drt2 = second_tap_response_start - stop_signal_onset
            actual_drt2s.append(actual_drt2)
        # Stats
        self.ideal_drt2_stats = {
            'min': min(ideal_drt2s),
            'max': max(ideal_drt2s),
            'mean': statistics.mean(ideal_drt2s),
        }
        self.actual_drt2_stats = {
            'min': min(actual_drt2s),
            'max': max(actual_drt2s),
            'mean': statistics.mean(actual_drt2s),
        }

    def populate_spreadsheet(self, spreadsheet):
        spreadsheet.select_sheet('DRT2')

        spreadsheet.set_values(['Ideal DRT2'])
        spreadsheet.set_values(['Min', self.ideal_drt2_stats['min']])
        spreadsheet.set_values(['Max', self.ideal_drt2_stats['max']])
        spreadsheet.set_values(['Mean', self.ideal_drt2_stats['mean']], advance_by_rows=2)

        spreadsheet.set_values(['Actual DRT2'])
        spreadsheet.set_values(['Min', self.actual_drt2_stats['min']])
        spreadsheet.set_values(['Max', self.actual_drt2_stats['max']])
        spreadsheet.set_values(['Mean', self.actual_drt2_stats['mean']])
