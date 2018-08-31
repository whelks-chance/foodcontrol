import re

from .dataextractor import DataExtractor


class AbstractQuestionnaireExtractor:

    @staticmethod
    def can_process_data_with_pattern(data, pattern):
        data_keys = data.keys()
        for data_key in data_keys:
            if re.match(pattern, data_key):
                return True
        return False


class FreqExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'FREQ[12345]-1?\d')


class TasteExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'TASTE[12345]-1?\d')


class AttractExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'ATTRACT[12345]-1?\d')


class EXExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EX-[AF]')


class WillExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'WILL[MT]')


class MoodExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MOOD[DAS]')


class IMPExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'IMP[AMN]')


class FoodIMPExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'FOODIMP')


class EMREGExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EMREG[NGIASC]')


class GoalsExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'GOALS')


class IntentExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'INTENT-[UH]')


class PersonExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'PERSON[NEOAC]')


class EffectExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EFFECT-[HUW]')


class MINDFExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MINDF')


class RESTRExtractor(AbstractQuestionnaireExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'RESTR')


class TellUsMoreDataExtractor(DataExtractor):

    type = 'tellusmore'

    fields = []

    question_extractors = [
        FreqExtractor(),
        TasteExtractor(),
        AttractExtractor(),
        EXExtractor(),
        WillExtractor(),
        MoodExtractor(),
        IMPExtractor(),
        FoodIMPExtractor(),
        EMREGExtractor(),
        GoalsExtractor(),
        IntentExtractor(),
        PersonExtractor(),
        EffectExtractor(),
        MINDFExtractor(),
        RESTRExtractor(),
    ]

    def get_question_extractor(self, row):
        for question_extractor in self.question_extractors:
            data = row['data']
            if question_extractor.can_process_data(data):
                return question_extractor
        return None

    def extract(self, row):
        question_extractor = self.get_question_extractor(row)
        if question_extractor:
            print('row is', type(question_extractor).__name__)
        else:
            print('no QE for row:', row['type'])

    def check(self, row):
        pass

    def calculate(self, row):
        pass
