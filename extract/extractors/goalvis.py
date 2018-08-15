from .dataextractor import DataExtractor


class GoalVisDataExtractor(DataExtractor):

    type = 'GOALVIS'

    fields = [
        ('Goal 1', 'data.goals.0.goal', ),
        ('Goal 1 Likelihood', 'data.goals.0.goal-likelihood', ),
        ('Goal 1 Visualise Time', 'data.goals.0.visualiseTime', ),
        ('Goal 1 Visualise Points', 'data.goals.0.visualisePoints', ),

        ('Goal 2', 'data.goals.1.goal', ),
        ('Goal 2 Likelihood', 'data.goals.1.goal-likelihood', ),
        ('Goal 2 Visualise Time', 'data.goals.1.visualiseTime', ),
        ('Goal 2 Visualise Points', 'data.goals.1.visualisePoints', ),
    ]

    def check(self, row):

        def check_session_score():
            session_score = self.value(row, 'data.sessionScore')
            if session_score is not None:
                goal_1_visualise_points = self.value(row, 'data.goals.0.visualisePoints')
                goal_2_visualise_points = self.value(row, 'data.goals.1.visualisePoints')
                assert session_score == goal_1_visualise_points + goal_2_visualise_points

        check_session_score()
