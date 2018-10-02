from .questiondataextractor import QuestionDataExtractor


class MajorCharacterQuestionDataExtractor(QuestionDataExtractor):
    """
    A major character question has a pattern of the form: MOODD, MOODA and MOODS
    i.e. a question prefix, e.g. WILL, MOOD and IMP, followed by a major character
    e.g. ['D', 'A', 'S']
    """

    def __init__(self):
        super().__init__()
        self.major_keypaths = self.create_major_keypaths(self.value_keypaths)
        print(self.major_keypaths)

    def create_major_keypaths(self, keypaths):
        major_keypaths = []
        for major in self.major_characters:
            key = '{}{}'.format(self.prefix, major)
            key_keypaths = []
            major_keypaths.append(key_keypaths)
            for keypath in keypaths:
                major_keypath = '.'.join(['data', key, keypath[0]])
                new_keypath = list(keypath)
                new_keypath[0] = major_keypath
                key_keypaths.append(new_keypath)
        return major_keypaths

    def get_value_keypaths(self):
        return self.major_keypaths


class WillQuestionDataExtractor(MajorCharacterQuestionDataExtractor):

    prefix = 'WILL'
    major_characters = ['M', 'T']

    number_of_scores = 6

    value_keypaths = [
        ('answers.S1.answer', 'S1'),
        ('answers.S2.answer', 'S2'),
        ('answers.S3.answer', 'S3'),
        ('answers.S4.answer', 'S4'),
        ('answers.S5.answer', 'S5'),
        ('answers.S6.answer', 'S6'),
    ]

    def get_derived_value_keypaths(self):
        return [
            ('S1', 'S1 Score', self.code_response_reversed),
            ('S2', 'S2 Score', self.code_response_reversed),
            ('S3', 'S3 Score', self.code_response),
            ('S4', 'S4 Score', self.code_response),
            ('S5', 'S5 Score', self.code_response_reversed),
            ('S6', 'S6 Score', self.code_response),
            (None, 'Sum Scores', self.calculate_sum_scores),
            (None, 'Missing Scores', self.calculate_missing_scores),
        ]

    @staticmethod
    def code_response(response_value):
        coding_scheme = {
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
        }
        return coding_scheme[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        coding_scheme = {
            '1': 6,
            '2': 5,
            '3': 4,
            '4': 3,
            '5': 2,
            '6': 1,
        }
        return coding_scheme[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'WILL[MT]')


class MoodQuestionDataExtractor(MajorCharacterQuestionDataExtractor):

    prefix = 'MOOD'
    major_characters = ['D', 'A', 'S']

    number_of_scores = 16

    value_keypaths = [
        ('answers.S1.answer', 'S1'),
        ('answers.S2.answer', 'S2'),
        ('answers.S3.answer', 'S3'),
        ('answers.S4.answer', 'S4'),
        ('answers.S5.answer', 'S5'),
        ('answers.S6.answer', 'S6'),
        ('answers.S7.answer', 'S7'),
        ('answers.S8.answer', 'S8'),
        ('answers.S9.answer', 'S9'),
        ('answers.S10.answer', 'S10'),
        ('answers.S11.answer', 'S11'),
        ('answers.S12.answer', 'S12'),
        ('answers.S13.answer', 'S13'),
        ('answers.S14.answer', 'S14'),
        ('answers.S15.answer', 'S15'),
        ('answers.S16.answer', 'S16'),
        ('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self):
        return [
            ('S1', 'S1 Score', self.code_response),
            ('S2', 'S2 Score', self.code_response),
            ('S3', 'S3 Score', self.code_response),
            ('S4', 'S4 Score', self.code_response),
            ('S5', 'S5 Score', self.code_response),
            ('S6', 'S6 Score', self.code_response),
            ('S7', 'S7 Score', self.code_response),
            ('S8', 'S8 Score', self.code_response_reversed),
            ('S9', 'S9 Score', self.code_response),
            ('S10', 'S10 Score', self.code_response_reversed),
            ('S11', 'S11 Score', self.code_response),
            ('S12', 'S12 Score', self.code_response_reversed),
            ('S13', 'S13 Score', self.code_response),
            ('S14', 'S14 Score', self.code_response_reversed),
            ('S15', 'S15 Score', self.code_response_reversed),
            ('S16', 'S16 Score', self.code_response_reversed),
            # (None, 'Sum Scores', self.calculate_sum_scores),
            # (None, 'Missing Scores', self.calculate_missing_scores),
        ]

    @staticmethod
    def code_response(response_value):
        coding_scheme = {
            '1': 1,
            '0': 0,
        }
        return coding_scheme[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        coding_scheme = {
            '1': 0,
            '0': 1,
        }
        return coding_scheme[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MOOD[DAS]')


# TODO: Handle different scoring systems for different major characters
class IMPQuestionDataExtractor(MajorCharacterQuestionDataExtractor):

    prefix = 'IMP'
    major_characters = ['A', 'M', 'N']

    number_of_scores = 7

    value_keypaths = [
        ('answers.S1.answer', 'S1'),
        ('answers.S2.answer', 'S2'),
        ('answers.S3.answer', 'S3'),
        ('answers.S4.answer', 'S4'),
        ('answers.S5.answer', 'S5'),
        ('answers.S6.answer', 'S6'),
        ('answers.S7.answer', 'S7'),
        ('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self):
        return [
            ('S1', 'S1 Score', self.code_response),
            ('S2', 'S2 Score', self.code_response),
            ('S3', 'S3 Score', self.code_response),
            ('S4', 'S4 Score', self.code_response),
            ('S5', 'S5 Score', self.code_response),
            ('S6', 'S6 Score', self.code_response),
            ('S7', 'S7 Score', self.code_response),
            (None, 'Sum Scores', self.calculate_sum_scores),
            (None, 'Missing Scores', self.calculate_missing_scores),
        ]

    @staticmethod
    def code_response(response_value):
        coding_scheme = {
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
        }
        return coding_scheme[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        coding_scheme = {
            '1': 4,
            '2': 3,
            '3': 2,
            '4': 1,
        }
        return coding_scheme[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'IMP[AMN]')


class EMREGQuestionDataExtractor(MajorCharacterQuestionDataExtractor):

    prefix = 'EMREG'
    major_characters = ['N', 'G', 'I', 'A', 'S', 'C']

    number_of_scores = 8

    value_keypaths = [
        ('answers.S1.answer', 'S1'),
        ('answers.S2.answer', 'S2'),
        ('answers.S3.answer', 'S3'),
        ('answers.S4.answer', 'S4'),
        ('answers.S5.answer', 'S5'),
        ('answers.S6.answer', 'S6'),
        ('answers.S7.answer', 'S7'),
        ('answers.S8.answer', 'S8'),
        ('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self):
        return [
            ('S1', 'S1 Score', self.code_response),
            ('S2', 'S2 Score', self.code_response),
            ('S3', 'S3 Score', self.code_response),
            ('S4', 'S4 Score', self.code_response),
            ('S5', 'S5 Score', self.code_response),
            ('S6', 'S6 Score', self.code_response),
            ('S7', 'S7 Score', self.code_response),
            ('S8', 'S8 Score', self.code_response),
            (None, 'Sum Scores', self.calculate_sum_scores),
            (None, 'Missing Scores', self.calculate_missing_scores),
        ]

    @staticmethod
    def code_response(response_value):
        coding_scheme = {
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
        }
        return coding_scheme[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        coding_scheme = {
            '1': 5,
            '2': 4,
            '3': 3,
            '4': 2,
            '5': 1,
        }
        return coding_scheme[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EMREG[NGIASC]')


class PersonQuestionDataExtractor(MajorCharacterQuestionDataExtractor):

    prefix = 'PERSON'
    major_characters = ['N', 'E', 'O', 'A', 'C']

    number_of_scores = 10

    value_keypaths = [
        ('answers.S1.answer', 'S1'),
        ('answers.S2.answer', 'S2'),
        ('answers.S3.answer', 'S3'),
        ('answers.S4.answer', 'S4'),
        ('answers.S5.answer', 'S5'),
        ('answers.S6.answer', 'S6'),
        ('answers.S7.answer', 'S7'),
        ('answers.S8.answer', 'S8'),
        ('answers.S9.answer', 'S9'),
        ('answers.S10.answer', 'S10'),
        ('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self):
        return [
            ('S1', 'S1 Score', self.code_response),
            ('S2', 'S2 Score', self.code_response),
            ('S3', 'S3 Score', self.code_response),
            ('S4', 'S4 Score', self.code_response),
            ('S5', 'S5 Score', self.code_response),
            ('S6', 'S6 Score', self.code_response),
            ('S7', 'S7 Score', self.code_response),
            ('S8', 'S8 Score', self.code_response),
            ('S9', 'S9 Score', self.code_response),
            ('S10', 'S10 Score', self.code_response),
            (None, 'Sum Scores', self.calculate_sum_scores),
            (None, 'Missing Scores', self.calculate_missing_scores),
        ]

    @staticmethod
    def code_response(response_value):
        coding_scheme = {
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
        }
        return coding_scheme[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        coding_scheme = {
            '1': 5,
            '2': 4,
            '3': 3,
            '4': 2,
            '5': 1,
        }
        return coding_scheme[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'PERSON[NEOAC]')


class EffectQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'EFFECT'

    def get_value_keypaths(self):
        return [
            ('EFFECT-H.answers.healthy.answer', 'H Answer'),
            ('EFFECT-H.timeOnQuestion', 'H Time on Question'),
            ('EFFECT-U.answers.unhealthy.answer', 'U Answer'),
            ('EFFECT-U.timeOnQuestion', 'U Time on Question'),
            ('EFFECT-W.answers.weight.answer', 'W Answer'),
            ('EFFECT-W.timeOnQuestion', 'W Time on Question'),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EFFECT-[HUW]')


class RESTRQuestionDataExtractor(MajorCharacterQuestionDataExtractor):

    prefix = 'RESTR-'
    major_characters = ['C', 'W']

    number_of_scores = 6

    value_keypaths = [
        ('answers.S1.answer', 'S1'),
        ('answers.S2.answer', 'S2'),
        ('answers.S3.answer', 'S3'),
        ('answers.S4.answer', 'S4'),
        ('answers.S5.answer', 'S5'),
        ('answers.S6.answer', 'S6'),
        ('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self):
        return [
            (None, 'Sum Scores', self.calculate_sum_scores),
            (None, 'Missing Scores', self.calculate_missing_scores),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'RESTR-[CW]')
