from utils import irange

from .questiondataextractor import QuestionDataExtractor

from keypath_extractor import Keypath


class MajorMinorQuestionDataExtractor(QuestionDataExtractor):
    """
    A major minor question has a pattern of the form: FREQ1-1, FREQ1-2, FREQ1-3
    i.e. a question prefix, e.g. FREQ, TASTE and ATTRACT, followed by a major number
    in the range 1...n followed by a dash followed by a minor number in the range 1...m
    In the examples seen so far, n = 5 and m = 12
    """

    def __init__(self):
        super().__init__()
        self.major_minor_keypaths = self.create_major_minor_keypaths(self.value_keypaths)

    def create_major_minor_keypaths(self, keypaths):
        major_minor_keypaths = []
        for major in self.major_range:
            for minor in self.minor_range:
                key = '{}{}-{}'.format(self.prefix, major, minor)
                key_keypaths = []
                major_minor_keypaths.append(key_keypaths)
                for keypath in keypaths:
                    major_keypath = '.'.join(['data', key, keypath.source_keypath])
                    new_keypath = Keypath(major_keypath, keypath.destination_keypath, is_optional=keypath.is_optional,
                                          transformer_fn=keypath.transformer_fn)
                    # new_keypath = list(keypath)
                    # new_keypath[0] = major_keypath
                    key_keypaths.append(new_keypath)
        return major_minor_keypaths

    def get_value_keypaths(self):
        return self.major_minor_keypaths

    def can_process_data(self, data):
        pattern = self.prefix + r'[12345]-1?\d'
        return self.can_process_data_with_pattern(data, pattern)


class FreqQuestionDataExtractor(MajorMinorQuestionDataExtractor):

    prefix = 'FREQ'
    major_range = irange(1, 5)
    minor_range = irange(1, 12)

    value_keypaths = [
        Keypath('answers.FE.answer', 'FE'),
        Keypath('answers.FC.answer', 'FC Answer'),
        Keypath('answers.FC.sliderValue', 'FC Slider Value'),
        Keypath('VsmInfo.id', 'ID'),
        Keypath('VsmInfo.type', 'Type'),
        Keypath('VsmInfo.selected', 'Selected'),
        Keypath('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self, row=None):
        return [
            Keypath('FE', 'FE Score', self.code_answer),
            Keypath('FC Answer', 'FC Score', self.code_answer),
            Keypath('Type', 'Type Value', self.code_food_type),
            Keypath('Selected', 'Selected Value', self.code_food_selected),
        ]

    @staticmethod
    def code_food_type(food_value):
        coding_scheme = {
            None: None,
            'U': 0,
            'H': 1,
        }
        return coding_scheme[food_value]

    @staticmethod
    def code_food_selected(food_selected_value):
        coding_scheme = {
            None: None,
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
            None: None,
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

    value_keypaths = [
        Keypath('answers.0.answer', 'FE'),
        Keypath('VsmInfo.id', 'ID'),
        Keypath('VsmInfo.type', 'Type'),
        Keypath('VsmInfo.selected', 'Selected'),
        Keypath('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self, row=None):
        return [
            Keypath('Type', 'Type Value', self.code_food_type),
            Keypath('Selected', 'Selected Value', self.code_food_selected),
        ]

    @staticmethod
    def code_food_type(food_value):
        coding_scheme = {
            None: None,
            'U': 0,
            'H': 1,
        }
        return coding_scheme[food_value]

    @staticmethod
    def code_food_selected(food_selected_value):
        coding_scheme = {
            None: None,
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

    value_keypaths = [
        Keypath('answers.0.answer', 'FE'),
        Keypath('VsmInfo.id', 'ID'),
        Keypath('VsmInfo.type', 'Type'),
        Keypath('VsmInfo.selected', 'Selected'),
        Keypath('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self, row=None):
        return [
            Keypath('Type', 'Type Value', self.code_food_type),
            Keypath('Selected', 'Selected Value', self.code_food_selected),
        ]

    @staticmethod
    def code_food_type(food_value):
        coding_scheme = {
            None: None,
            'U': 0,
            'H': 1,
        }
        return coding_scheme[food_value]

    @staticmethod
    def code_food_selected(food_selected_value):
        coding_scheme = {
            None: None,
            'Selected': 1,
            'MB':       2,
            'upload':   3,
            'random':   4,
            'add':      5,
        }
        return coding_scheme[food_selected_value]
