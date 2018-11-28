from ..gamedataextractor import GameDataExtractor


from .points_checker import PointsChecker
from .ssrt_calculator import SSRTCalculator
from .trial_count_checker import TrialCountChecker
from .trial_types_counter import TrialTypesCounter
from .value_labels_checker import ValueLabelChecker
from .tap_response_checker import TapResponseChecker
from .durations_calculator import DurationsCalculator
from .raw_events_calculator import RawEventsCalculator
from .dependent_variables_calculator import DependentVariablesCalculator
from .double_points_checker import DoublePointsChecker
from .double_tap_response_checker import DoubleTapResponseChecker
from .drt2_calculator import DRT2Calculator

from spreadsheet import Spreadsheet
from keypath_extractor import Keypath


class AbstractStopDataExtractor(GameDataExtractor):
    """The abstract base class for all STOP games"""

    @staticmethod
    def get_value_keypaths():
        return [
            Keypath('data.captureDate', 'Capture Date'),
        ]

    spreadsheet = None

    def clear(self):
        pass

    def check(self, row):
        super(AbstractStopDataExtractor, self).check(row)

    def calculate(self, row):
        super(AbstractStopDataExtractor, self).calculate(row)

        self.spreadsheet = Spreadsheet()
        for evaluator in self.evaluators():
            evaluator.evaluate(row)
            evaluator.populate_spreadsheet(self.spreadsheet)
            if evaluator.has_session_log_entries():
                evaluator.session_event_log.print()

    def evaluators(self):
        return self.common_evaluators() + self.custom_evaluators()

    @staticmethod
    def common_evaluators():
        return [
            DurationsCalculator(),
            TrialCountChecker(),
            ValueLabelChecker(),
            TrialTypesCounter(),
            DependentVariablesCalculator(),
            RawEventsCalculator(),
        ]

    @staticmethod
    def custom_evaluators():
        return [
            PointsChecker(),
            TapResponseChecker(),
            SSRTCalculator(),
        ]


class StopDataExtractor(AbstractStopDataExtractor):

    type = 'STOP'


class RestraintDataExtractor(AbstractStopDataExtractor):

    type = 'RESTRAINT'


class NAStopDataExtractor(AbstractStopDataExtractor):

    type = 'NASTOP'


class NARestraintDataExtractor(AbstractStopDataExtractor):

    type = 'NARESTRAINT'


class GStopDataExtractor(AbstractStopDataExtractor):

    type = 'GSTOP'


class GRestraintDataExtractor(AbstractStopDataExtractor):

    type = 'GRESTRAINT'


class DoubleDataExtractor(AbstractStopDataExtractor):

    type = 'DOUBLE'

    @staticmethod
    def custom_evaluators():
        return [
            DoublePointsChecker(),
            DoubleTapResponseChecker(),
            DRT2Calculator(),
        ]
