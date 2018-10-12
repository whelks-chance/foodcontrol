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
    add_sum_scores_and_missing_scores_columns = True

    value_keypaths = [
        ('answers.S1.answer', 'S1'),
        ('answers.S2.answer', 'S2'),
        ('answers.S3.answer', 'S3'),
        ('answers.S4.answer', 'S4'),
        ('answers.S5.answer', 'S5'),
        ('answers.S6.answer', 'S6'),
    ]

    def get_derived_value_keypaths(self, row=None):
        return [
            ('S1', 'S1 Score', self.code_response_reversed),
            ('S2', 'S2 Score', self.code_response_reversed),
            ('S3', 'S3 Score', self.code_response),
            ('S4', 'S4 Score', self.code_response),
            ('S5', 'S5 Score', self.code_response_reversed),
            ('S6', 'S6 Score', self.code_response),
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

    number_of_scores = 7
    add_sum_scores_and_missing_scores_columns = True

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


class IMPQuestionDataExtractor(MajorCharacterQuestionDataExtractor):

    prefix = 'IMP'
    major_characters = ['A', 'M', 'N']

    number_of_scores = 11
    add_sum_scores_and_missing_scores_columns = True

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
        ('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self, row=None):
        row_type = None
        if row:
            if 'IMPN' in row['data']:
                row_type = 'N'
            elif 'IMPM' in row['data']:
                row_type = 'M'
            elif 'IMPA' in row['data']:
                row_type = 'M'
        if row_type == 'A':
            # print('A derived value keypaths')
            return [
                ('S1', 'S1 Score', self.code_response),
                ('S2', 'S2 Score', self.code_response),
                ('S3', 'S3 Score', self.code_response_reversed),
                ('S4', 'S4 Score', self.code_response),
                ('S5', 'S5 Score', self.code_response_reversed),
                ('S6', 'S6 Score', self.code_response),
                ('S7', 'S7 Score', self.code_response),
                ('S8', 'S8 Score', self.code_response),
                ('S9', 'S9 Score', self.blank),
                ('S10', 'S10 Score', self.blank),
                ('S11', 'S11 Score', self.blank),
            ]
        if row_type == 'M':
            # print('M derived value keypaths')
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
                ('S11', 'S11 Score', self.code_response_reversed),
            ]
        if row_type is None or row_type == 'N':
            # print('N derived value keypaths')
            return [
                ('S1', 'S1 Score', self.code_response_reversed),
                ('S2', 'S2 Score', self.code_response_reversed),
                ('S3', 'S3 Score', self.code_response_reversed),
                ('S4', 'S4 Score', self.code_response_reversed),
                ('S5', 'S5 Score', self.code_response_reversed),
                ('S6', 'S6 Score', self.code_response_reversed),
                ('S7', 'S7 Score', self.code_response),
                ('S8', 'S8 Score', self.code_response_reversed),
                ('S9', 'S9 Score', self.code_response),
                ('S10', 'S10 Score', self.code_response),
                ('S11', 'S11 Score', self.code_response_reversed),
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

    @staticmethod
    def blank(response_value):
        return None

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'IMP[AMN]')


class EMREGQuestionDataExtractor(MajorCharacterQuestionDataExtractor):

    prefix = 'EMREG'
    major_characters = ['N', 'G', 'I', 'A', 'S', 'C']

    number_of_scores = 8
    add_sum_scores_and_missing_scores_columns = True

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

    def get_derived_value_keypaths(self, row=None):
        return [
            ('S1', 'S1 Score', self.code_response),
            ('S2', 'S2 Score', self.code_response),
            ('S3', 'S3 Score', self.code_response),
            ('S4', 'S4 Score', self.code_response),
            ('S5', 'S5 Score', self.code_response),
            ('S6', 'S6 Score', self.code_response),
            ('S7', 'S7 Score', self.code_response),
            ('S8', 'S8 Score', self.code_response),
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
    add_sum_scores_and_missing_scores_columns = True

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

    def get_derived_value_keypaths(self, row=None):
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


class RESTRQuestionDataExtractor(MajorCharacterQuestionDataExtractor):

    prefix = 'RESTR-'
    major_characters = ['C', 'W']

    number_of_scores = 6
    add_sum_scores_and_missing_scores_columns = True

    value_keypaths = [
        ('answers.S1.answer', 'S1'),
        ('answers.S2.answer', 'S2'),
        ('answers.S3.answer', 'S3'),
        ('answers.S4.answer', 'S4'),
        ('answers.S5.answer', 'S5'),
        ('answers.S6.answer', 'S6'),
        ('timeOnQuestion', 'Time On Question'),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'RESTR-[CW]')
