from utils import KeypathDict, irange

from .questiondataextractor import QuestionDataExtractor


class MajorMinorQuestionDataExtractor(QuestionDataExtractor):
    """
    A major minor question has a pattern of the form: FREQ1-1, FREQ1-2, FREQ1-3
    i.e. a question prefix, e.g. FREQ, TASTE and ATTRACT, followed by a major number
    in the range 1...n followed by a dash followed by a minor number in the range 1...m
    In the examples seen so far, n = 5 and m = 12
    """

    def extract(self, row):
        self.rows = []
        print('------------------------------------->MajorMinorQuestionExtractor.extract()')
        print(self.major_range, self.minor_range)
        print(row)
        data = row['data']
        for major in self.major_range:
            for minor in self.minor_range:
                key = '{}{}-{}'.format(self.prefix, major, minor)
                try:
                    key_data = KeypathDict(data[key])
                    print(key, '->', key_data)
                    values = {}
                    self.extract_field_values(self._fields(), key_data, values)
                    self.calculate_derived_field_values(values)
                    print("WITH DERIVED: ", values)
                    self.rows.append(values)
                except KeyError as e:
                    print(e)

    def can_process_data(self, data):
        pattern = self.prefix + r'[12345]-1?\d'
        return self.can_process_data_with_pattern(data, pattern)


class FreqQuestionDataExtractor(MajorMinorQuestionDataExtractor):

    prefix = 'FREQ'
    major_range = irange(1, 5)
    minor_range = irange(1, 12)

    fields = [
        ('FE', 'answers.FE.answer'),
        ('FC Answer', 'answers.FC.answer'),
        ('FC Slider Value', 'answers.FC.sliderValue'),
        ('ID', 'VsmInfo.id'),
        ('Type', 'VsmInfo.type'),
        ('Selected', 'VsmInfo.selected'),
        ('Time On Question', 'timeOnQuestion'),
    ]

    derived_fields = [
        ('FE', 'FE Score', 'code_answer'),
        ('FC Answer', 'FC Score', 'code_answer'),
        ('Type', 'Type Value', 'code_food_type'),
        ('Selected', 'Selected Value', 'code_food_selected'),
    ]

    @staticmethod
    def code_food_type(food_value):
        coding_scheme = {
            'U': 0,
            'H': 1,
        }
        return coding_scheme[food_value]

    @staticmethod
    def code_food_selected(food_selected_value):
        coding_scheme = {
            'Selected': 1,
            'MB':       2,
            'upload':   3,
            'random':   4,
            'add':      5,
        }
        return coding_scheme[food_selected_value]

    @staticmethod
    def code_answer(answer_value):
        coding_scheme = {
            'None':      0,
            '1-2 times': 1,
            '3-4 times': 2,
            '5-6 times': 3,
            '7+ times':  4,
        }
        return coding_scheme[answer_value]


class TasteQuestionDataExtractor(MajorMinorQuestionDataExtractor):

    prefix = 'TASTE'
    major_range = irange(1, 5)
    minor_range = irange(1, 12)

    fields = [
        ('FE', 'answers.0.answer'),
        ('ID', 'VsmInfo.id'),
        ('Type', 'VsmInfo.type'),
        ('Selected', 'VsmInfo.selected'),
        ('Time On Question', 'timeOnQuestion'),
    ]

    derived_fields = [
        ('Type', 'Type Value', 'code_food_type'),
        ('Selected', 'Selected Value', 'code_food_selected'),
    ]

    @staticmethod
    def code_food_type(food_value):
        coding_scheme = {
            'U': 0,
            'H': 1,
        }
        return coding_scheme[food_value]

    @staticmethod
    def code_food_selected(food_selected_value):
        coding_scheme = {
            'Selected': 1,
            'MB':       2,
            'upload':   3,
            'random':   4,
            'add':      5,
        }
        return coding_scheme[food_selected_value]


class AttractQuestionDataExtractor(MajorMinorQuestionDataExtractor):

    prefix = 'ATTRACT'
    major_range = irange(1, 5)
    minor_range = irange(1, 12)

    fields = [
        ('FE', 'answers.0.answer'),
        ('ID', 'VsmInfo.id'),
        ('Type', 'VsmInfo.type'),
        ('Selected', 'VsmInfo.selected'),
        ('Time On Question', 'timeOnQuestion'),
    ]

    derived_fields = [
        ('Type', 'Type Value', 'code_food_type'),
        ('Selected', 'Selected Value', 'code_food_selected'),
    ]

    @staticmethod
    def code_food_type(food_value):
        coding_scheme = {
            'U': 0,
            'H': 1,
        }
        return coding_scheme[food_value]

    @staticmethod
    def code_food_selected(food_selected_value):
        coding_scheme = {
            'Selected': 1,
            'MB':       2,
            'upload':   3,
            'random':   4,
            'add':      5,
        }
        return coding_scheme[food_selected_value]
