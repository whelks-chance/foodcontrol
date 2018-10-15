from .gamedataextractor import GameDataExtractor

from keypath_extractor import Keypath


class MCIIDataExtractor(GameDataExtractor):

    type = 'MCII'

    @staticmethod
    def get_value_keypaths():
        return [
            # Plan 0
            Keypath('data.plans.0.ifCode', 'Plan 1 If Code'),
            Keypath('data.plans.0.ifStatement', 'Plan 1 If Statement'),
            Keypath('data.plans.0.ifOption', 'Plan 1 If Option'),
            Keypath('data.plans.0.then', 'Plan 1 Then'),
            Keypath('data.plans.0.thenCode', 'Plan 1 Then Code'),
            Keypath('data.plans.0.thenOption', 'Plan 1 The Option'),
            Keypath('data.plans.0.visualiseTime', 'Plan 1 Visualise Time'),
            Keypath('data.plans.0.visualisePoints', 'Plan 1 Visualise Points'),
            # Plan 1
            Keypath('data.plans.1.ifCode', 'Plan 2 If Code'),
            Keypath('data.plans.1.ifStatement', 'Plan 2 If Statement'),
            Keypath('data.plans.1.ifOption', 'Plan 2 If Option'),
            Keypath('data.plans.1.then', 'Plan 2 Then'),
            Keypath('data.plans.1.thenCode', 'Plan 2 Then Code'),
            Keypath('data.plans.1.thenOption', 'Plan 2 The Option'),
            Keypath('data.plans.1.visualiseTime', 'Plan 2 Visualise Time'),
            Keypath('data.plans.1.visualisePoints', 'Plan 2 Visualise Points'),
            # There is occasionally more than 1 goal but there should only ever be one goal
            # More than one goal is a data output error so handle this by using the first element
            Keypath('data.goals.0.goal', 'Goal'),
            Keypath('data.goals.0.goal-likelihood', 'Goal Likelihood'),
            Keypath('data.goals.0.outcome-thoughts', 'Outcome Thoughts'),
            Keypath('data.goals.0.obstacle', 'Obstacle'),
            Keypath('data.goals.0.obstacle-thoughts', 'Obstacle Thoughts'),
        ]

    def check(self, row):

        def check_session_score():
            session_score = self.get_keypath_value(row, 'data.sessionScore')
            if session_score is not None:
                plan_1_visualise_points = self.get_keypath_value(row, 'data.plans.0.visualisePoints')
                plan_2_visualise_points = self.get_keypath_value(row, 'data.plans.1.visualisePoints')
                assert session_score == plan_1_visualise_points + plan_2_visualise_points

        check_session_score()
