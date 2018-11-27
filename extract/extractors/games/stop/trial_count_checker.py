from utils import get_session_events


class TrialCountChecker:

    def __init__(self):
        pass

    def check_trials_count(self, row):
        number_of_rounds = 4
        old_number_of_trials = 48
        new_number_of_trials = 24
        session_events = get_session_events(row)
        assert len(session_events) == (number_of_rounds * old_number_of_trials)\
            or (number_of_rounds * new_number_of_trials)

    check_trials_count()
