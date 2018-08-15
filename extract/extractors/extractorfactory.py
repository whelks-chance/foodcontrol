from .stop import StopDataExtractor, RestraintDataExtractor, NAStopDataExtractor, GStopDataExtractor
from .stop import GRestraintDataExtractor, NARestraintDataExtractor, DoubleDataExtractor
from .mcii import MCIIDataExtractor
from .goalvis import GoalVisDataExtractor
from .measures import MeasuresDataExtractor
from .eligibility import EligibilityDataExtractor
from .additionalinfo import AdditionalInfoDataExtractor
from .virtualsupermarket import VirtualSupermarketDataExtractor


class ExtractorFactory:

    extractors = [
        StopDataExtractor(),
        RestraintDataExtractor(),
        NAStopDataExtractor(),
        NARestraintDataExtractor(),
        GStopDataExtractor(),
        GRestraintDataExtractor(),
        DoubleDataExtractor(),
        MCIIDataExtractor(),
        GoalVisDataExtractor(),
        MeasuresDataExtractor(),
        EligibilityDataExtractor(),
        AdditionalInfoDataExtractor(),
        VirtualSupermarketDataExtractor(),
    ]

    def __init__(self):
        self.extractors_by_type = {extractor.type:extractor for extractor in self.extractors}

    def extractor_for_row_type(self, row_type):
        if row_type in self.extractors_by_type:
            return self.extractors_by_type[row_type]
        else:
            raise ValueError("No extractor for type '{}'".format(row_type))

