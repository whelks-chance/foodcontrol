from utils import get_session_events

from .abstract_stop_evaluator import AbstractStopEvaluator


class TrialCountChecker(AbstractStopEvaluator):

    def __init__(self):
        pass

    def evaluate(self, row):
        self.check_trials_count(row)

    @staticmethod
    def check_trials_count(row):
        number_of_rounds = 4
        old_number_of_trials = 48  # App data version 1 had 48 trials...
        new_number_of_trials = 24  # ...now its 24 trials
        session_events = get_session_events(row)
        assert len(session_events) == (number_of_rounds * old_number_of_trials)\
            or (number_of_rounds * new_number_of_trials)
