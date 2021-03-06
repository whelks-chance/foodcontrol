import re

from utils import irange

from extractors.dataextractor import DataExtractor

from keypath_extractor import Keypath


class QuestionDataExtractor(DataExtractor):
    """The abstract base class for all questionnaire data extractors"""

    type = 'tellusmore'

    def __init__(self):
        super().__init__()
        self.csv_rows = []

    def get_filename(self):
        return 'Q-{}'.format(self.prefix)

    def get_common_keypaths(self):
        return super().get_common_keypaths() + [
            Keypath('data.TUMsessionID', 'TUM Session ID'),
        ]

    def get_value_keypaths_for_naming_columns(self):
        if hasattr(self, 'value_keypaths'):
            keypaths = self.value_keypaths
        else:
            keypaths = self.get_value_keypaths()
        if self.should_add_sum_scores_and_missing_scores_columns():
            return keypaths + [
                # The source keypath of 'Does not matter' is a placeholder because
                # we're only using the destination keypath to get the column name
                Keypath('Does not matter', 'Sum Scores'),
                Keypath('Does not matter', 'Missing Scores'),
            ]
        return keypaths

    def can_process_row(self, row):
        return super().can_process_row(row) and self.can_process_data(row['data'])

    def get_column_names(self):
        return super().get_column_names() + self.get_question_type_column_names()

    @staticmethod
    def can_process_data_with_pattern(data, pattern):
        data_keys = data.keys()
        for data_key in data_keys:
            if re.match(pattern, data_key):
                print('QUESTION: ', data_key)
                return True
        return False

    def extract_values(self, data):
        value_keypaths = self.get_value_keypaths()
        if not self.keypaths_are_nested(value_keypaths):
            values = super().extract_values(data)
            values = [self.add_calculations(values[0])]
            prefixes = self.get_question_type_prefixes(value_keypaths[0].source_keypath)
            values = self.add_question_type_column_names(values, prefixes)
            return values

        rows = []
        common_keypaths = self.get_common_keypaths()
        nested_value_keypaths = value_keypaths
        derived_value_keypaths = self.get_derived_value_keypaths(data)
        for value_keypaths in nested_value_keypaths:
            all_value_keypaths = common_keypaths + value_keypaths
            values = self.extract_values_with_keypaths(all_value_keypaths, derived_value_keypaths, data)
            values = self.add_calculations(values)
            prefixes = self.get_question_type_prefixes(value_keypaths[0].source_keypath)
            values = self.add_question_type_column_names(values, prefixes)
            rows.append(values)
        return rows

    def add_calculations(self, values):
        if self.should_add_sum_scores_and_missing_scores_columns():
            sum_scores = DataExtractor.EMPTY_CELL_VALUE
            missing_scores = DataExtractor.EMPTY_CELL_VALUE
            if values:
                sum_scores = self.calculate_sum_scores(values, self.number_of_scores)
                missing_scores = self.calculate_missing_scores(values, self.number_of_scores)
            values['Sum Scores'] = sum_scores
            values['Missing Scores'] = missing_scores
        return values

    def should_add_sum_scores_and_missing_scores_columns(self):
        return hasattr(self, 'add_sum_scores_and_missing_scores_columns') and self.add_sum_scores_and_missing_scores_columns

    def has_subtype(self):
        """
        Questions with a subtype, e.g. WILL[MT] and FREQ[1-5]-[1-12], have a nested keypath
        structure - one list of keypaths per subtype - so need to be handled differently.
        Major Character and Major Minor questions have subtypes. Most questions do have a
        subtype so questions without a subtype are explicitly marked with a no-subtype property
        with a True value.
        """
        return not hasattr(self, 'no_subtype')

    def get_question_type_column_names(self):
        """Return ['QType', 'Sub QType'] for a question with a subtype; ['QType'] otherwise"""
        column_names = ['QType']
        if self.has_subtype():
            column_names += ['Sub QType']
        return column_names

    def get_question_type_prefixes(self, keypath):
        """
        Return a (prefix, character) tuple for the string source keypath,
        e.g. data.EFFECT-A -> ('EFFECT', 'A')
        """
        paths = keypath.split('.')
        question_type = paths[1]
        if '-' in question_type:
            # e.g. EFFECT-A -> 'EFFECT', 'A'
            return question_type.split('-')
        elif not self.has_subtype():
            # GOALS -> 'GOALS', None
            return question_type, None
        else:
            # e.g. PERSONN -> 'PERSON', 'N'
            return question_type[:-1], question_type[-1:]

    def add_question_type_column_names(self, values, prefixes):
        if type(values) is list:
            values[0]['QType'] = prefixes[0]
            if self.has_subtype():
                values[0]['Sub QType'] = prefixes[1]
            return values
        else:
            values['QType'] = prefixes[0]
            if self.has_subtype():
                values['Sub QType'] = prefixes[1]
            return values

    def extract_row_data(self, row):
        self.csv_rows = self.extract_values(row)

    @staticmethod
    def score_column_name_sequence(number_of_scores):
        """
        Create a list of column names for a set of extracted scores,
        e.g. for 4 scores the list would be ['S1', 'S2', 'S3', 'S4']
        These are used to access the scores when creating the sum
        and counting the number of missing scores.
        """
        return ['S' + str(response) for response in irange(1, number_of_scores)]

    def calculate_sum_scores(self, values, number_of_scores):
        sum_scores = 0
        column_names_to_count = self.score_column_name_sequence(number_of_scores)
        for column_name in column_names_to_count:
            if column_name in values:
                score = values[column_name]
                if score and score != DataExtractor.EMPTY_CELL_VALUE:
                    sum_scores += int(score)  # Scores may appear as quoted numbers
        return sum_scores

    def calculate_missing_scores(self, values, number_of_scores):
        sum_missing = 0
        for column_name in self.score_column_name_sequence(number_of_scores):
            if column_name in values:
                value = values[column_name]
                if value == DataExtractor.EMPTY_CELL_VALUE or value is None:
                    sum_missing += 1
        return sum_missing

    @staticmethod
    def blank(response_value):
        """A placeholder method that does nothing that's used when a method is required"""
        return None


class EXQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'EX'
    no_subtype = True

    def get_value_keypaths(self):
        return [
            Keypath('data.EX-A.answers.0.answer', 'EX A Answer'),
            Keypath('data.EX-A.timeOnQuestion', 'EX A Time On Question'),
            Keypath('data.EX-F.answers.exercise-times-moderate.answer', 'EX F Times Moderate'),
            Keypath('data.EX-F.answers.exercise-times-vigorous.answer', 'EX F Times Vigorous'),
            Keypath('data.EX-F.answers.exercise-times-strengthening.answer', 'EX F Times Strengthening'),
            Keypath('data.EX-F.answers.exercise-minutes-moderate.answer', 'EX F Minutes Moderate'),
            Keypath('data.EX-F.answers.exercise-minutes-vigorous.answer', 'EX F Minutes Vigorous'),
            Keypath('data.EX-F.answers.exercise-minutes-strengthening.answer', 'EX F Minutes Strengthening'),
        ]

    def get_derived_value_keypaths(self, row=None):
        return [
            Keypath('EX A Answer', 'EX A Answer Score', self.code_response),
        ]

    @staticmethod
    def code_response(response_value):
        coding_scheme = {
            None:                              None,
            'I am inactive':                   0,
            'My activity levels are low':      1,
            'My activity levels are moderate': 2,
        }
        return coding_scheme[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EX-[AF]')


class FoodIMPQuestionExtractor(QuestionDataExtractor):

    prefix = 'FOODIMP'
    no_subtype = True

    number_of_scores = 16
    add_sum_scores_and_missing_scores_columns = True

    def get_value_keypaths(self):
        return [
            Keypath('data.FOODIMP.answers.S1.answer', 'S1'),
            Keypath('data.FOODIMP.answers.S2.answer', 'S2'),
            Keypath('data.FOODIMP.answers.S3.answer', 'S3'),
            Keypath('data.FOODIMP.answers.S4.answer', 'S4'),
            Keypath('data.FOODIMP.answers.S5.answer', 'S5'),
            Keypath('data.FOODIMP.answers.S6.answer', 'S6'),
            Keypath('data.FOODIMP.answers.S7.answer', 'S7'),
            Keypath('data.FOODIMP.answers.S8.answer', 'S8'),
            Keypath('data.FOODIMP.answers.S9.answer', 'S9'),
            Keypath('data.FOODIMP.answers.S10.answer', 'S10'),
            Keypath('data.FOODIMP.answers.S11.answer', 'S11'),
            Keypath('data.FOODIMP.answers.S12.answer', 'S12'),
            Keypath('data.FOODIMP.answers.S13.answer', 'S13'),
            Keypath('data.FOODIMP.answers.S14.answer', 'S14'),
            Keypath('data.FOODIMP.answers.S15.answer', 'S15'),
            Keypath('data.FOODIMP.answers.S16.answer', 'S16'),
            Keypath('data.FOODIMP.timeOnQuestion', 'Time On Question'),
        ]

    def get_derived_value_keypaths(self, row=None):
        return [
            Keypath('S1',  'S1 Score', self.code_response),
            Keypath('S2',  'S2 Score', self.code_response),
            Keypath('S3',  'S3 Score', self.code_response),
            Keypath('S4',  'S4 Score', self.code_response),
            Keypath('S5',  'S5 Score', self.code_response),
            Keypath('S6',  'S6 Score', self.code_response),
            Keypath('S7',  'S7 Score', self.code_response),
            Keypath('S8',  'S8 Score', self.code_response_reversed),
            Keypath('S9',  'S9 Score', self.code_response),
            Keypath('S10', 'S10 Score', self.code_response_reversed),
            Keypath('S11', 'S11 Score', self.code_response),
            Keypath('S12', 'S12 Score', self.code_response_reversed),
            Keypath('S13', 'S13 Score', self.code_response),
            Keypath('S14', 'S14 Score', self.code_response_multiple),
            Keypath('S15', 'S15 Score', self.code_response_multiple),
            Keypath('S16', 'S16 Score', self.code_response_multiple),
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

    @staticmethod
    def code_response_multiple(response_value):
        coding_scheme = {
            None: None,
            '0': 0,
            '1': 0,
            '2': 1,
            '3': 1,
        }
        return coding_scheme[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'FOODIMP')


class GoalsQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'GOALS'
    no_subtype = True

    def get_value_keypaths(self):
        return [
            Keypath('data.GOALS.answers.ideal-weight.answer.unit1_val', 'Ideal Weight Unit 1 Value'),
            Keypath('data.GOALS.answers.ideal-weight.answer.unit2_val', 'Ideal Weight Unit 2 Value'),
            Keypath('data.GOALS.answers.ideal-weight.answer.units', 'Ideal Weight Units'),
            Keypath('data.GOALS.answers.achievable-weight.answer.unit1_val', 'Achievable Weight Unit 1 Value'),
            Keypath('data.GOALS.answers.achievable-weight.answer.unit2_val', 'Achievable Weight Unit 2 Value'),
            Keypath('data.GOALS.answers.achievable-weight.answer.units', 'Achievable Weight Units'),
            Keypath('data.GOALS.answers.happy-weight.answer.unit1_val', 'Happy Weight Unit 1 Value'),
            Keypath('data.GOALS.answers.happy-weight.answer.unit2_val', 'Happy Weight Unit 2 Value'),
            Keypath('data.GOALS.answers.happy-weight.answer.units', 'Happy Weight Units'),
            Keypath('data.GOALS.timeOnQuestion', 'Time On Question'),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'GOALS')


class IntentQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'INTENT'
    no_subtype = True

    def get_value_keypaths(self):
        return [
            Keypath('data.INTENT-H.answers.healthy-foods.answer', 'Healthy Foods Answer'),
            Keypath('data.INTENT-H.timeOnQuestion', 'Healthy Foods Answer'),
            Keypath('data.INTENT-U.answers.unhealthy-foods.answer', 'Unhealthy Foods Answer'),
            Keypath('data.INTENT-U.timeOnQuestion', 'Unhealthy Foods Answer'),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'INTENT-[UH]')


class EffectQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'EFFECT'
    no_subtype = True

    def get_value_keypaths(self):
        return [
            Keypath('data.EFFECT-H.answers.healthy.answer', 'H Answer'),
            Keypath('data.EFFECT-H.timeOnQuestion', 'H Time on Question'),
            Keypath('data.EFFECT-U.answers.unhealthy.answer', 'U Answer'),
            Keypath('data.EFFECT-U.timeOnQuestion', 'U Time on Question'),
            Keypath('data.EFFECT-W.answers.weight.answer', 'W Answer'),
            Keypath('data.EFFECT-W.timeOnQuestion', 'W Time on Question'),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EFFECT-[HUW]')


class MINDFQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'MINDF'
    no_subtype = True

    number_of_scores = 15
    add_sum_scores_and_missing_scores_columns = True

    def get_value_keypaths(self):
        return [
            Keypath('data.MINDF.answers.S1.answer', 'S1'),
            Keypath('data.MINDF.answers.S2.answer', 'S2'),
            Keypath('data.MINDF.answers.S3.answer', 'S3'),
            Keypath('data.MINDF.answers.S4.answer', 'S4'),
            Keypath('data.MINDF.answers.S5.answer', 'S5'),
            Keypath('data.MINDF.answers.S6.answer', 'S6'),
            Keypath('data.MINDF.answers.S7.answer', 'S7'),
            Keypath('data.MINDF.answers.S8.answer', 'S8'),
            Keypath('data.MINDF.answers.S9.answer', 'S9'),
            Keypath('data.MINDF.answers.S10.answer', 'S10'),
            Keypath('data.MINDF.answers.S11.answer', 'S11'),
            Keypath('data.MINDF.answers.S12.answer', 'S12'),
            Keypath('data.MINDF.answers.S13.answer', 'S13'),
            Keypath('data.MINDF.answers.S14.answer', 'S14'),
            Keypath('data.MINDF.answers.S15.answer', 'S15'),
            Keypath('data.MINDF.timeOnQuestion', 'Time On Question'),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MINDF')
