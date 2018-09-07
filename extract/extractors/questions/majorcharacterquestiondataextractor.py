from utils import KeypathDict

from .questiondataextractor import QuestionDataExtractor


class MajorCharacterQuestionDataExtractor(QuestionDataExtractor):
    """
    A major character question has a pattern of the form: MOODD, MOODA and MOODS
    i.e. a question prefix, e.g. WILL, MOOD and IMP, followed by a major character
    e.g. ['D', 'A', 'S']
    """

    def extract(self, row):
        self.rows = []
        data = row['data']
        for major in self.major_characters:
            key = '{}{}'.format(self.prefix, major)
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


class WillQuestionDataExtractor(MajorCharacterQuestionDataExtractor):

    prefix = 'WILL'
    major_characters = ['M', 'T']

    number_of_scores = 6

    fields = [
        ('S1', 'answers.S1.answer'),
        ('S2', 'answers.S2.answer'),
        ('S3', 'answers.S3.answer'),
        ('S4', 'answers.S4.answer'),
        ('S5', 'answers.S5.answer'),
        ('S6', 'answers.S6.answer'),
    ]

    derived_fields = [
        ('S1', 'S1 Score', 'code_response_reversed'),
        ('S2', 'S2 Score', 'code_response_reversed'),
        ('S3', 'S3 Score', 'code_response'),
        ('S4', 'S4 Score', 'code_response'),
        ('S5', 'S5 Score', 'code_response_reversed'),
        ('S6', 'S6 Score', 'code_response'),
        (None, 'Sum Scores', 'calculate_sum_scores'),
        (None, 'Missing Scores', 'calculate_missing_scores'),
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

    fields = [
        ('S1',  'answers.S1.answer'),
        ('S2',  'answers.S2.answer'),
        ('S3',  'answers.S3.answer'),
        ('S4',  'answers.S4.answer'),
        ('S5',  'answers.S5.answer'),
        ('S6',  'answers.S6.answer'),
        ('S7',  'answers.S7.answer'),
        ('S8',  'answers.S8.answer'),
        ('S9',  'answers.S9.answer'),
        ('S10', 'answers.S10.answer'),
        ('S11', 'answers.S11.answer'),
        ('S12', 'answers.S12.answer'),
        ('S13', 'answers.S13.answer'),
        ('S14', 'answers.S14.answer'),
        ('S15', 'answers.S15.answer'),
        ('S16', 'answers.S16.answer'),
        ('Time On Question', 'timeOnQuestion'),
    ]

    derived_fields = [
        ('S1', 'S1 Score', 'code_response'),
        ('S2', 'S2 Score', 'code_response'),
        ('S3', 'S3 Score', 'code_response'),
        ('S4', 'S4 Score', 'code_response'),
        ('S5', 'S5 Score', 'code_response'),
        ('S6', 'S6 Score', 'code_response'),
        ('S7', 'S7 Score', 'code_response'),
        ('S8', 'S8 Score', 'code_response_reversed'),
        ('S9', 'S9 Score', 'code_response'),
        ('S10', 'S10 Score', 'code_response_reversed'),
        ('S11', 'S11 Score', 'code_response'),
        ('S12', 'S12 Score', 'code_response_reversed'),
        ('S13', 'S13 Score', 'code_response'),
        ('S14', 'S14 Score', 'code_response_reversed'),
        ('S15', 'S15 Score', 'code_response_reversed'),
        ('S16', 'S16 Score', 'code_response_reversed'),
        (None, 'Sum Scores', 'calculate_sum_scores'),
        (None, 'Missing Scores', 'calculate_missing_scores'),
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

    fields = [
        ('S1', 'answers.S1.answer'),
        ('S2', 'answers.S2.answer'),
        ('S3', 'answers.S3.answer'),
        ('S4', 'answers.S4.answer'),
        ('S5', 'answers.S5.answer'),
        ('S6', 'answers.S6.answer'),
        ('S7', 'answers.S7.answer'),
        ('Time On Question', 'MOODD.timeOnQuestion'),
    ]

    derived_fields = [
        ('S1', 'S1 Score', 'code_response'),
        ('S2', 'S2 Score', 'code_response'),
        ('S3', 'S3 Score', 'code_response'),
        ('S4', 'S4 Score', 'code_response'),
        ('S5', 'S5 Score', 'code_response'),
        ('S6', 'S6 Score', 'code_response'),
        ('S7', 'S7 Score', 'code_response'),
        (None, 'Sum Scores', 'calculate_sum_scores'),
        (None, 'Missing Scores', 'calculate_missing_scores'),
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

    fields = [
        ('S1', 'answers.S1.answer'),
        ('S2', 'answers.S2.answer'),
        ('S3', 'answers.S3.answer'),
        ('S4', 'answers.S4.answer'),
        ('S5', 'answers.S5.answer'),
        ('S6', 'answers.S6.answer'),
        ('S7', 'answers.S7.answer'),
        ('S8', 'answers.S8.answer'),
        ('Time on Question', 'timeOnQuestion'),
    ]

    derived_fields = [
        ('S1', 'S1 Score', 'code_response'),
        ('S2', 'S2 Score', 'code_response'),
        ('S3', 'S3 Score', 'code_response'),
        ('S4', 'S4 Score', 'code_response'),
        ('S5', 'S5 Score', 'code_response'),
        ('S6', 'S6 Score', 'code_response'),
        ('S7', 'S7 Score', 'code_response'),
        ('S8', 'S8 Score', 'code_response'),
        (None, 'Sum Scores', 'calculate_sum_scores'),
        (None, 'Missing Scores', 'calculate_missing_scores'),
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

    fields = [
        ('S1', 'answers.S1.answer'),
        ('S2', 'answers.S2.answer'),
        ('S3', 'answers.S3.answer'),
        ('S4', 'answers.S4.answer'),
        ('S5', 'answers.S5.answer'),
        ('S6', 'answers.S6.answer'),
        ('S7', 'answers.S7.answer'),
        ('S8', 'answers.S8.answer'),
        ('S9', 'answers.S9.answer'),
        ('S10', 'answers.S10.answer'),
        ('Time On Question', 'timeOnQuestion'),
    ]

    derived_fields = [
        ('S1', 'S1 Score', 'code_response'),
        ('S2', 'S2 Score', 'code_response'),
        ('S3', 'S3 Score', 'code_response'),
        ('S4', 'S4 Score', 'code_response'),
        ('S5', 'S5 Score', 'code_response'),
        ('S6', 'S6 Score', 'code_response'),
        ('S7', 'S7 Score', 'code_response'),
        ('S8', 'S8 Score', 'code_response'),
        ('S9', 'S6 Score', 'code_response'),
        ('S10', 'S7 Score', 'code_response'),
        (None, 'Sum Scores', 'calculate_sum_scores'),
        (None, 'Missing Scores', 'calculate_missing_scores'),
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

    fields = [
        ('H Answer', 'EFFECT-H.answers.healthy.answer'),
        ('H Time on Question', 'EFFECT-H.timeOnQuestion'),
        ('U Answer', 'EFFECT-U.answers.unhealthy.answer'),
        ('U Time on Question', 'EFFECT-U.timeOnQuestion'),
        ('W Answer', 'EFFECT-W.answers.weight.answer'),
        ('W Time on Question', 'EFFECT-W.timeOnQuestion'),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EFFECT-[HUW]')


class RESTRQuestionDataExtractor(MajorCharacterQuestionDataExtractor):

    prefix = 'RESTR-'
    major_characters = ['C', 'W']

    number_of_scores = 6

    fields = [
        ('S1', 'answers.S1.answer'),
        ('S2', 'answers.S2.answer'),
        ('S3', 'answers.S3.answer'),
        ('S4', 'answers.S4.answer'),
        ('S5', 'answers.S5.answer'),
        ('S6', 'answers.S6.answer'),
        ('Time on Question', 'timeOnQuestion'),
    ]

    derived_fields = [
        (None, 'Sum Scores', 'calculate_sum_scores'),
        (None, 'Missing Scores', 'calculate_missing_scores'),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'RESTR-[CW]')
