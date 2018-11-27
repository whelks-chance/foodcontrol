from .abstract_stop_evaluator import AbstractStopEvaluator

from utils import get_session_events


class DRT2Calculator(AbstractStopEvaluator):

    def __init__(self):
        self.ideal_drt2 = None
        self.actual_drt2 = None

    def evaluate(self, row):
        session_events = get_session_events(row)
        self.ideal_drt2 = 0
        self.actual_drt2 = 0

    def populate_spreadsheet(self, spreadsheet):
        spreadsheet.select_sheet('DRT2')
        spreadsheet.set_values(['Ideal DRT2', self.ideal_drt2])
        spreadsheet.set_values(['Actual DRT2', self.actual_drt2])
