import re

from .dataextractor import DataExtractor

from keypathdict import KeypathDict


def irange(start, end):
    """Return a range that includes the end value: 1,5 -> 1...5 rather than 1...4"""
    return range(start, end + 1)


class AbstractQuestionExtractor:

    values = {}

    def can_process_data(self, data):
        """Create a pattern that matches a question prefix with major and minor numbers"""
        pattern = self.prefix + r'[12345]-1?\d'
        return self.can_process_data_with_pattern(data, pattern)

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


class MajorMinorQuestionExtractor(AbstractQuestionExtractor):
    """
    A major minor question has a pattern of the form: FREQ1-1, FREQ1-2, FREQ1-3
    i.e. a question prefix, e.g. FREQ, TASTE and ATTRACT, followed by a major number
    in the range 1...n followed by a dash followed by a minor number in the range 1...m
    In the examples seen so far, n = 5 and m = 12
    """

    def extract(self, data):
        """Store the column value for each keypath"""
        self.clear()
        for major in self.major_range:
            for minor in self.minor_range:
                key = '{}{}-{}'.format(self.prefix, major, minor)
                try:
                    key_data = KeypathDict(data[key])
                    print(key, '->', key_data)
                    self.extract_key_data(key_data)
                except KeyError:
                    pass

    def extract_key_data(self, key_data):
        for column_name, keypath, code in self.fields:
            value = key_data.get_keypath_value(keypath)
            # print('--->', column_name, keypath, value)
            self.values[column_name] = value
            if code:
                self.code_value(*code, value)

    def code_value(self, code_column_name, code_function_name, value):
        # print('Call "{}()" to get value for "{}"'.format(code_function_name, code_column_name))
        code_function = getattr(self, code_function_name)
        code_value = code_function(value)
        # print('"{}()" -> {}'.format(code_function_name, code_value))
        self.values[code_column_name] = code_value


class FreqExtractor(MajorMinorQuestionExtractor):

    prefix = 'FREQ'
    major_range = irange(1, 5)
    minor_range = irange(1, 12)

    fields = (
        ('FE', 'answers.FE.answer', ('FE Score', 'code_answer'), ),
        ('FC Answer', 'answers.FC.answer', ('FC Score', 'code_answer'), ),
        ('FC Slider Value', 'answers.FC.sliderValue', None, ),
        ('ID', 'VsmInfo.id', None, ),
        ('Type', 'VsmInfo.type', ('Type Value', 'code_food_type'),),
        ('Selected', 'VsmInfo.selected', ('Selected Value', 'code_food_selected'),),
        ('Time On Question', 'timeOnQuestion', None, ),
    )

    @staticmethod
    def code_food_type(food_value):
        food_type_codes = {
            'U': 0,
            'H': 1,
        }
        return food_type_codes[food_value]

    @staticmethod
    def code_food_selected(food_selected_value):
        food_selected_codes = {
            'Selected': 1,
            'MB':       2,
            'upload':   3,
            'random':   4,
            'add':      5,
        }
        return food_selected_codes[food_selected_value]

    @staticmethod
    def code_answer(answer_value):
        answer_codes = {
            'None':      0,
            '1-2 times': 1,
            '3-4 times': 2,
            '5-6 times': 3,
            '7+ times':  4,
        }
        return answer_codes[answer_value]


class TasteExtractor(MajorMinorQuestionExtractor):

    fields = (
        ('FE', 'answers.FE.answer', None, ),
        ('ID', 'VsmInfo.id', None, ),
        ('Type', 'VsmInfo.type', None, ),
        ('Selected', 'VsmInfo.selected', None, ),
        ('Time On Question', 'timeOnQuestion', None, ),
    )

    major_range = irange(1, 5)
    minor_range = irange(1, 12)
    prefix = 'TASTE'


class AttractExtractor(MajorMinorQuestionExtractor):

    fields = (
        ('FE', 'answers.FE.answer', None, ),
        ('ID', 'VsmInfo.id', None, ),
        ('Type', 'VsmInfo.type', None, ),
        ('Selected', 'VsmInfo.selected', None, ),
        ('Time On Question', 'timeOnQuestion', None, ),
    )

    major_range = irange(1, 5)
    minor_range = irange(1, 12)
    prefix = 'ATTRACT'


class EXExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EX-[AF]')


class WillExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'WILL[MT]')


class MoodExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MOOD[DAS]')


class IMPExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'IMP[AMN]')


class FoodIMPExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'FOODIMP')


class EMREGExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EMREG[NGIASC]')


class GoalsExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'GOALS')


class IntentExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'INTENT-[UH]')


class PersonExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'PERSON[NEOAC]')


class EffectExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EFFECT-[HUW]')


class MINDFExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MINDF')


class RESTRExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'RESTR')


class TellUsMoreDataExtractor(DataExtractor):

    type = 'tellusmore'

    fields = []

    question_extractors = [
        FreqExtractor(),
        TasteExtractor(),
        AttractExtractor(),
        # EXExtractor(),
        # WillExtractor(),
        # MoodExtractor(),
        # IMPExtractor(),
        # FoodIMPExtractor(),
        # EMREGExtractor(),
        # GoalsExtractor(),
        # IntentExtractor(),
        # PersonExtractor(),
        # EffectExtractor(),
        # MINDFExtractor(),
        # RESTRExtractor(),
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
