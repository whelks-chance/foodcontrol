from collections import defaultdict

from utils import get_keypath_value

from .abstract_stop_evaluator import AbstractStopEvaluator


class RawEventsCalculator(AbstractStopEvaluator):

    def __init__(self):
        self.raw_count = {
            'on': defaultdict(int),
            'off': defaultdict(int)
        }

    def evaluate(self, row):
        self.count_raw_events(row)

    def count_raw_events(self, row):
        raw_events = get_keypath_value(row, 'data.0.rawEvents')
        for raw_event in raw_events:
            self.raw_count['on'][raw_event['eventOn']] += 1
            self.raw_count['off'][raw_event['eventOff']] += 1
