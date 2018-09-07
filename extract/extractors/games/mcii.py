from .gamedataextractor import GameDataExtractor


class MCIIDataExtractor(GameDataExtractor):

    type = 'MCII'

    fields = [
        ('Plan 1 If Code', 'data.plans.0.ifCode'),
        ('Plan 1 If Statement', 'data.plans.0.ifStatement'),
        ('Plan 1 If Option', 'data.plans.0.ifOption'),
        ('Plan 1 Then', 'data.plans.0.then'),
        ('Plan 1 Then Code', 'data.plans.0.thenCode'),
        ('Plan 1 The Option', 'data.plans.0.thenOption'),
        ('Plan 1 Visualise Time', 'data.plans.0.visualiseTime'),
        ('Plan 1 Visualise Points', 'data.plans.0.visualisePoints'),

        ('Plan 2 If Code', 'data.plans.1.ifCode',),
        ('Plan 2 If Statement', 'data.plans.1.ifStatement',),
        ('Plan 2 If Option', 'data.plans.1.ifOption',),
        ('Plan 2 Then', 'data.plans.1.then',),
        ('Plan 2 Then Code', 'data.plans.1.thenCode',),
        ('Plan 2 The Option', 'data.plans.1.thenOption',),
        ('Plan 2 Visualise Time', 'data.plans.1.visualiseTime',),
        ('Plan 2 Visualise Points', 'data.plans.1.visualisePoints',),

        # There is occasionally more than 1 goal but there should only ever be one goal
        # More than one goal is a data output error so handle this by using the first element
        ('Goal', 'data.goals.0.goal'),
        ('Goal Likelihood', 'data.goals.0.goal-likelihood'),
        ('Outcome Thoughts', 'data.goals.0.outcome-thoughts'),
        ('Obstacle', 'data.goals.0.obstacle'),
        ('Obstacle Thoughts', 'data.goals.0.obstacle-thoughts'),
    ]

    def check(self, row):

        def check_session_score():
            session_score = row.get_keypath_value('data.sessionScore')
            if session_score is not None:
                plan_1_visualise_points = row.get_keypath_value('data.plans.0.visualisePoints')
                plan_2_visualise_points = row.get_keypath_value('data.plans.1.visualisePoints')
                assert session_score == plan_1_visualise_points + plan_2_visualise_points

        check_session_score()
