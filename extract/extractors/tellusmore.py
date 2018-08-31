import re

from .dataextractor import DataExtractor

from keypathdict import KeypathDict


def irange(start, end):
    return range(start, end + 1)


class AbstractQuestionnaireExtractor:

    values = {}

    @staticmethod
    def can_process_data_with_pattern(data, pattern):
        data_keys = data.keys()
        for data_key in data_keys:
            if re.match(pattern, data_key):
                return True
        return False

    def clear(self):
        """Reset common value and calculation stores. Override to to reset type-specific value and calculation stores"""
        self.values.clear()

    def extract(self, data):
        """Store the column value for each keypath"""
        self.clear()
        # print(data)
        for freq_major in irange(1, 5):
            for freq_minor in irange(1, 12):
                freq_key = 'FREQ{}-{}'.format(freq_major, freq_minor)
                # print(freq_key)
                try:
                    freq_data = data[freq_key]
                    print(freq_key, '->', freq_data)
                    for column_name, keypath in self.fields:
                        print(column_name, keypath)
                        value = data.get_keypath_value(keypath)
                        self.values[column_name] = value
                except KeyError:
                    pass
                    # print(freq_key, '->', 'None')


class FreqExtractor(AbstractQuestionnaireExtractor):

    fields = (
        ('FE', 'answers.FE.answer', ),
        ('FC', 'answers.FC.answer', ),
        ('FC Slider Value', 'answers.FC.sliderValue', ),
        ('ID', 'VsmInfo.id', ),
        ('Type', 'VsmInfo.type', ),
        ('Selected', 'VsmInfo.selected', ),
        ('Time On Question', 'timeOnQuestion', ),
    )

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

    def get_question_extractor(self, data):
        for question_extractor in self.question_extractors:
            if question_extractor.can_process_data(data):
                return question_extractor
        return None

    def extract(self, row):
        data = KeypathDict(row['data'])
        question_extractor = self.get_question_extractor(data)
        if question_extractor:
            print('row is', type(question_extractor).__name__)
            question_extractor.extract(data)
            print('values =', question_extractor.values)
        else:
            print('no QE for row:', row['type'])

    def check(self, row):
        pass

    def calculate(self, row):
        pass
