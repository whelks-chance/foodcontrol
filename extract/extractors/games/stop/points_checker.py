from .abstract_stop_evaluator import AbstractStopEvaluator


class PointsChecker(AbstractStopEvaluator):

    def check_points(self, row):
        points = {
            'GO': {
                'CORRECT_GO': 20,
                'INCORRECT_GO': -50,
                'MISS_GO': -20,
            },
            'STOP': {
                'CORRECT_STOP': 50,
                'INCORRECT_STOP': -50,
                'MISS_STOP': -50,
            }
        }
        running_total = 0
        session_events = self.get_session_events(row)
        for session_event in session_events:
            trial_type = session_event['trialType']
            tap_response_type = session_event['tapResponseType']
            points_this_trial = session_event['pointsThisTrial']
            assert points_this_trial == points[trial_type][tap_response_type]
            running_total += points_this_trial
            points_running_total = session_event['pointsRunningTotal']
            assert points_running_total == running_total

    def evaluate(self, row):
        self.check_points(row)
