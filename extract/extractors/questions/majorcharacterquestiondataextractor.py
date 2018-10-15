from .questiondataextractor import QuestionDataExtractor

from keypath_extractor import Keypath


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
                major_keypath = '.'.join(['data', key, keypath.source_keypath])
                new_keypath = Keypath(major_keypath, keypath.destination_keypath, is_optional=keypath.is_optional,
                                      transformer_fn=keypath.transformer_fn)
                # new_keypath = list(keypath)
                # new_keypath[0] = major_keypath
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
        Keypath('answers.S1.answer', 'S1'),
        Keypath('answers.S2.answer', 'S2'),
        Keypath('answers.S3.answer', 'S3'),
        Keypath('answers.S4.answer', 'S4'),
        Keypath('answers.S5.answer', 'S5'),
        Keypath('answers.S6.answer', 'S6'),
    ]

    def get_derived_value_keypaths(self, row=None):
        # row is None when asking for the keypaths for naming columns
        row_type = None  # row is None when asking for the keypaths for naming columns
        if row:
            if 'WILLM' in row['data']:
                row_type = 'M'
            elif 'WILLT' in row['data']:
                row_type = 'T'
        if row_type is None or row_type == 'M':
            # print('WILLM derived value keypaths')
            return [
                Keypath('S1', 'S1 Score', self.code_response_reversed),
                Keypath('S2', 'S2 Score', self.code_response_reversed),
                Keypath('S3', 'S3 Score', self.code_response),
                Keypath('S4', 'S4 Score', self.code_response),
                Keypath('S5', 'S5 Score', self.code_response_reversed),
                Keypath('S6', 'S6 Score', self.code_response),
            ]
        if row_type == 'T':
            # print('WILLT derived value keypaths')
            return [
                Keypath('S1', 'S1 Score', self.code_response_reversed),
                Keypath('S2', 'S2 Score', self.code_response_reversed),
                Keypath('S3', 'S3 Score', self.code_response),
                Keypath('S4', 'S4 Score', self.code_response_reversed),
                Keypath('S5', 'S5 Score', self.code_response),
                Keypath('S6', 'S6 Score', self.code_response),
            ]

    @staticmethod
    def code_response(response_value):
        coding_scheme = {
            None: None,
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
            None: None,
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
        Keypath('answers.S1.answer', 'S1'),
        Keypath('answers.S2.answer', 'S2'),
        Keypath('answers.S3.answer', 'S3'),
        Keypath('answers.S4.answer', 'S4'),
        Keypath('answers.S5.answer', 'S5'),
        Keypath('answers.S6.answer', 'S6'),
        Keypath('answers.S7.answer', 'S7'),
        Keypath('timeOnQuestion', 'Time On Question'),
    ]

    @staticmethod
    def code_response(response_value):
        coding_scheme = {
            None: None,
            '1': 1,
            '0': 0,
        }
        return coding_scheme[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        coding_scheme = {
            None: None,
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
        Keypath('answers.S1.answer', 'S1'),
        Keypath('answers.S2.answer', 'S2'),
        Keypath('answers.S3.answer', 'S3'),
        Keypath('answers.S4.answer', 'S4'),
        Keypath('answers.S5.answer', 'S5'),
        Keypath('answers.S6.answer', 'S6'),
        Keypath('answers.S7.answer', 'S7'),
        Keypath('answers.S8.answer', 'S8'),
        Keypath('answers.S9.answer', 'S9', is_optional=True),
        Keypath('answers.S10.answer', 'S10', is_optional=True),
        Keypath('answers.S11.answer', 'S11', is_optional=True),
        Keypath('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self, row=None):
        # row is None when asking for the keypaths for naming columns
        if row:
            data = row['data']
            if 'IMPA' in data:
                row_type = 'A'
            elif 'IMPM' in data:
                row_type = 'M'
            elif 'IMPN' in data:
                row_type = 'N'
        else:
            row_type = 'M'

        keypaths = {
            'A': [
                Keypath('S1', 'S1 Score', transformer_fn=self.code_response),
                Keypath('S2', 'S2 Score', transformer_fn=self.code_response),
                Keypath('S3', 'S3 Score', transformer_fn=self.code_response_reversed),
                Keypath('S4', 'S4 Score', transformer_fn=self.code_response),
                Keypath('S5', 'S5 Score', transformer_fn=self.code_response_reversed),
                Keypath('S6', 'S6 Score', transformer_fn=self.code_response),
                Keypath('S7', 'S7 Score', transformer_fn=self.code_response),
                Keypath('S8', 'S8 Score', transformer_fn=self.code_response),
                Keypath('S9', 'S9 Score', transformer_fn=self.blank),
                Keypath('S10', 'S10 Score', transformer_fn=self.blank),
                Keypath('S11', 'S11 Score', transformer_fn=self.blank),
            ],
            'M': [
                Keypath('S1', 'S1 Score', transformer_fn=self.code_response),
                Keypath('S2', 'S2 Score', transformer_fn=self.code_response),
                Keypath('S3', 'S3 Score', transformer_fn=self.code_response),
                Keypath('S4', 'S4 Score', transformer_fn=self.code_response),
                Keypath('S5', 'S5 Score', transformer_fn=self.code_response),
                Keypath('S6', 'S6 Score', transformer_fn=self.code_response),
                Keypath('S7', 'S7 Score', transformer_fn=self.code_response),
                Keypath('S8', 'S8 Score', transformer_fn=self.code_response),
                Keypath('S9', 'S9 Score', transformer_fn=self.code_response),
                Keypath('S10', 'S10 Score', transformer_fn=self.code_response),
                Keypath('S11', 'S11 Score', transformer_fn=self.code_response_reversed),
            ],
            'N': [
                Keypath('S1', 'S1 Score', transformer_fn=self.code_response_reversed),
                Keypath('S2', 'S2 Score', transformer_fn=self.code_response_reversed),
                Keypath('S3', 'S3 Score', transformer_fn=self.code_response_reversed),
                Keypath('S4', 'S4 Score', transformer_fn=self.code_response_reversed),
                Keypath('S5', 'S5 Score', transformer_fn=self.code_response_reversed),
                Keypath('S6', 'S6 Score', transformer_fn=self.code_response_reversed),
                Keypath('S7', 'S7 Score', transformer_fn=self.code_response),
                Keypath('S8', 'S8 Score', transformer_fn=self.code_response_reversed),
                Keypath('S9', 'S9 Score', transformer_fn=self.code_response),
                Keypath('S10', 'S10 Score', transformer_fn=self.code_response),
                Keypath('S11', 'S11 Score', transformer_fn=self.code_response_reversed),
            ]
        }
        return keypaths[row_type]

    @staticmethod
    def code_response(response_value):
        coding_scheme = {
            None: None,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
        }
        return coding_scheme[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        coding_scheme = {
            None: None,
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
    add_sum_scores_and_missing_scores_columns = True

    value_keypaths = [
        Keypath('answers.S1.answer', 'S1'),
        Keypath('answers.S2.answer', 'S2'),
        Keypath('answers.S3.answer', 'S3'),
        Keypath('answers.S4.answer', 'S4'),
        Keypath('answers.S5.answer', 'S5'),
        Keypath('answers.S6.answer', 'S6'),
        Keypath('answers.S7.answer', 'S7'),
        Keypath('answers.S8.answer', 'S8'),
        Keypath('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self, row=None):
        return [
            Keypath('S1', 'S1 Score', self.code_response),
            Keypath('S2', 'S2 Score', self.code_response),
            Keypath('S3', 'S3 Score', self.code_response),
            Keypath('S4', 'S4 Score', self.code_response),
            Keypath('S5', 'S5 Score', self.code_response),
            Keypath('S6', 'S6 Score', self.code_response),
            Keypath('S7', 'S7 Score', self.code_response),
            Keypath('S8', 'S8 Score', self.code_response),
        ]

    @staticmethod
    def code_response(response_value):
        coding_scheme = {
            None: None,
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
            None: None,
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
        Keypath('answers.S1.answer', 'S1'),
        Keypath('answers.S2.answer', 'S2'),
        Keypath('answers.S3.answer', 'S3'),
        Keypath('answers.S4.answer', 'S4'),
        Keypath('answers.S5.answer', 'S5'),
        Keypath('answers.S6.answer', 'S6'),
        Keypath('answers.S7.answer', 'S7'),
        Keypath('answers.S8.answer', 'S8'),
        Keypath('answers.S9.answer', 'S9'),
        Keypath('answers.S10.answer', 'S10'),
        Keypath('timeOnQuestion', 'Time On Question'),
    ]

    def get_derived_value_keypaths(self, row=None):
        return [
            Keypath('S1', 'S1 Score', self.code_response),
            Keypath('S2', 'S2 Score', self.code_response),
            Keypath('S3', 'S3 Score', self.code_response),
            Keypath('S4', 'S4 Score', self.code_response),
            Keypath('S5', 'S5 Score', self.code_response),
            Keypath('S6', 'S6 Score', self.code_response),
            Keypath('S7', 'S7 Score', self.code_response),
            Keypath('S8', 'S8 Score', self.code_response),
            Keypath('S9', 'S9 Score', self.code_response),
            Keypath('S10', 'S10 Score', self.code_response),
        ]

    @staticmethod
    def code_response(response_value):
        coding_scheme = {
            None: None,
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
            None: None,
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
        Keypath('answers.S1.answer', 'S1'),
        Keypath('answers.S2.answer', 'S2'),
        Keypath('answers.S3.answer', 'S3'),
        Keypath('answers.S4.answer', 'S4'),
        Keypath('answers.S5.answer', 'S5'),
        Keypath('answers.S6.answer', 'S6'),
        Keypath('timeOnQuestion', 'Time On Question'),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'RESTR-[CW]')
