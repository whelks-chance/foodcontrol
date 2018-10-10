from .games import *
from .questions import *


class ExtractorFactory:

    game_extractors = [
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

    question_extractors = [
        EXQuestionDataExtractor(),
        FoodIMPQuestionExtractor(),
        GoalsQuestionDataExtractor(),
        IntentQuestionDataExtractor(),
        EffectQuestionDataExtractor(),
        MINDFQuestionDataExtractor(),
        # Major Minor
        FreqQuestionDataExtractor(),
        TasteQuestionDataExtractor(),
        AttractQuestionDataExtractor(),
        # Major
        WillQuestionDataExtractor(),
        MoodQuestionDataExtractor(),
        IMPQuestionDataExtractor(),
        EMREGQuestionDataExtractor(),
        PersonQuestionDataExtractor(),
        RESTRQuestionDataExtractor(),
    ]

    extractors = game_extractors  # + question_extractors

    def __init__(self):
        self.extractors_by_type = {extractor.type: extractor for extractor in self.extractors}

    def extractor_for_row_type(self, row_type):
        if row_type in self.extractors_by_type:
            return self.extractors_by_type[row_type]
        else:
            raise ValueError("No extractor for type '{}'".format(row_type))

