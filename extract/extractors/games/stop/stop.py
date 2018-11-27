from ..gamedataextractor import GameDataExtractor
from ..session_event_log import SessionEventLog

from .raw_events_calculator import RawEventsCalculator
from .points_checker import PointsChecker
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
    session_event_log = SessionEventLog()

    def clear(self):
        pass

    def check(self, row):
        super(AbstractStopDataExtractor, self).check(row)

    def calculate(self, row):
        super(AbstractStopDataExtractor, self).calculate(row)

        evaluators = [
            RawEventsCalculator(),
            # PointsChecker(),
        ]

        self.spreadsheet = Spreadsheet()
        for evaluator in evaluators:
            evaluator.evaluate(row)
            evaluator.populate_spreadsheet(self.spreadsheet)

        # self.calculate_durations(row)
        # self.count_trial_and_types(row)
        # self.check_value_labels(row)
        # self.check_tap_responses(row)
        # self.check_points(row)
        # self.calculate_dependent_variables(row)
        # self.calculate_ssrt(row)
        # self.count_raw_events(row)
        # self.create_spreadsheet()

    # def create_spreadsheet(self):
    #     spreadsheet = Spreadsheet()


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

    def calculate(self, row):
        super(DoubleDataExtractor, self).calculate(row)

        evaluators = [
            DoublePointsChecker(),
            DoubleTapResponseChecker(),
            DRT2Calculator(),
        ]

        self.spreadsheet = Spreadsheet()
        for evaluator in evaluators:
            evaluator.evaluate(row)
            evaluator.populate_spreadsheet(self.spreadsheet)
