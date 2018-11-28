from .abstract_stop_evaluator import AbstractStopEvaluator
from ..session_event_log import SessionEventLog

from utils import get_session_events


class DoublePointsChecker(AbstractStopEvaluator):

    def __init__(self):
        self.session_event_log = SessionEventLog()

    def evaluate(self, row):
        self.check_points(row)

    def check_points(self, row):

        def check_go(initial_tap_response_type, second_tap_response_type):
            if (initial_tap_response_type, second_tap_response_type) == ('CORRECT_GO', 'N/A'):
                check_result = points_this_trial == 20
                # self.session_event_log.log_if_check_failed(check_result, session_event)
            elif (initial_tap_response_type, second_tap_response_type) == ('INCORRECT_GO', 'N/A'):
                check_result = points_this_trial == -20
                # self.session_event_log.log_if_check_failed(check_result, session_event)
            else:
                check_result = points_this_trial == -50
            self.session_event_log.log_if_check_failed(check_result, session_event)

        def check_double(initial_tap_response_type, second_tap_response_type):
            if (initial_tap_response_type, second_tap_response_type) == ('CORRECT', 'CORRECT'):
                check_result = points_this_trial == 50
                # self.session_event_log.log_if_check_failed(check_result, session_event)
            else:
                check_result = points_this_trial == -50
            self.session_event_log.log_if_check_failed(check_result, session_event)

        checks = {
            'GO': check_go,
            'DOUBLE': check_double,
        }

        running_total = 0
        session_events = get_session_events(row)
        for session_event in session_events:
            # Points Awarded
            trial_type = session_event['trialType']
            initial_tap_response_type = session_event['initialTapResponseType']
            second_tap_response_type = session_event['secondTapResponseType']
            points_this_trial = session_event['pointsThisTrial']
            checks[trial_type](initial_tap_response_type, second_tap_response_type)
            # Running Total
            running_total += points_this_trial
            points_running_total = session_event['pointsRunningTotal']
            check_passed = points_running_total == running_total
            self.session_event_log.log_if_check_failed(check_passed, session_event,
                                                       extra_message='points_running_total != running_total')
