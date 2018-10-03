import re

from utils import irange

from extractors.dataextractor import DataExtractor


class QuestionDataExtractor(DataExtractor):
    """The abstract base class for all questionnaire data extractors"""

    type = 'tellusmore'

    def __init__(self):
        super().__init__()
        self.csv_rows = []

    def get_filename(self):
        return '{}-{}'.format(self.type, self.prefix)

    def get_common_keypaths(self):
        return super().get_common_keypaths() + [
            ('data.TUMsessionID', 'TUM Session ID'),
        ]

    def get_value_keypaths_for_naming_columns(self):
        if hasattr(self, 'value_keypaths'):
            return self.value_keypaths
        else:
            return self.get_value_keypaths()

    def can_process_row(self, row):
        return super().can_process_row(row) and self.can_process_data(row['data'])

    def get_column_names(self):
        return super().get_column_names() + self.get_prefix_column_names()

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
            prefixes = self.get_prefixes(value_keypaths[0][0])
            values = self.add_prefixes(values, prefixes)
            return values

        rows = []
        common_keypaths = self.get_common_keypaths()
        nested_value_keypaths = value_keypaths
        derived_value_keypaths = self.get_derived_value_keypaths()
        for value_keypaths in nested_value_keypaths:
            all_value_keypaths = common_keypaths + value_keypaths
            values = self.extract_values_with_keypaths(all_value_keypaths, derived_value_keypaths, data)
            prefixes = self.get_prefixes(value_keypaths[0][0])
            values = self.add_prefixes(values, prefixes)
            rows.append(values)
        return rows

    def has_subtype(self):
        return not hasattr(self, 'no_subtype')

    def get_prefix_column_names(self):
        column_names = ['QType']
        if self.has_subtype():
            column_names += ['Sub QType']
        return column_names

    def get_prefixes(self, keypath):
        paths = keypath.split('.')
        question_type = paths[1]
        if '-' in question_type:
            return question_type.split('-')
        elif not self.has_subtype():
            return question_type, None
        else:
            return question_type[:-1], question_type[-1:]

    def add_prefixes(self, values, prefixes):
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

    def calculate(self, row):
        pass

    @staticmethod
    def calculate_sum_and_missing_scores(values, number_of_scores):
        print(values)
        scores_sum = 0
        missing_sum = 0
        # S1, S2, ...
        column_names = ['S' + str(response) for response in irange(1, number_of_scores)]
        for column_name in column_names:
            value = values[column_name]
            if value == DataExtractor.EMPTY_CELL_VALUE or value is None:
                missing_sum += 1
            else:
                print('column_name:', column_name)
                print('      value:', values[column_name])
                scores_sum += int(values[column_name])
        values['Scores Sum'] = scores_sum
        values['Num Missing'] = missing_sum

    @staticmethod
    def score_column_name_sequence(number_of_scores):
        return ['S' + str(response) + ' Score' for response in irange(1, number_of_scores)]

    def sum_scores(self, values, number_of_scores):
        sum_scores = 0
        for column_name in self.score_column_name_sequence(number_of_scores):
            score = values[column_name]
            if score and score != DataExtractor.EMPTY_CELL_VALUE:
                sum_scores += int(score)  # Scores may appear as quoted numbers
        return sum_scores

    def missing_scores(self, values, number_of_scores):
        sum_missing = 0
        for column_name in self.score_column_name_sequence(number_of_scores):
            value = values[column_name]
            if value == DataExtractor.EMPTY_CELL_VALUE or value is None:
                sum_missing += 1
        return sum_missing

    def calculate_sum_scores(self, values):
        return self.sum_scores(values, self.number_of_scores)

    def calculate_missing_scores(self, values):
        return self.missing_scores(values, self.number_of_scores)


class EXQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'EX'
    no_subtype = True

    def get_value_keypaths(self):
        return [
            ('data.EX-A.answers.0.answer', 'EX A Answer'),
            ('data.EX-A.timeOnQuestion', 'EX A Time On Question'),
            ('data.EX-F.answers.exercise-times-moderate.answer', 'EX F Times Moderate'),
            ('data.EX-F.answers.exercise-times-vigorous.answer', 'EX F Times Vigorous'),
            ('data.EX-F.answers.exercise-times-strengthening.answer', 'EX F Times Strengthening'),
            ('data.EX-F.answers.exercise-minutes-moderate.answer', 'EX F Minutes Moderate'),
            ('data.EX-F.answers.exercise-minutes-vigorous.answer', 'EX F Minutes Vigorous'),
            ('data.EX-F.answers.exercise-minutes-strengthening.answer', 'EX F Minutes Strengthening'),
        ]

    def get_derived_value_keypaths(self):
        return [
            ('EX A Answer', 'EX A Answer Score', self.code_answer),
        ]

    @staticmethod
    def code_answer(answer_value):
        coding_scheme = {
            'I am inactive':                   0,
            'My activity levels are low':      1,
            'My activity levels are moderate': 2,
        }
        return coding_scheme[answer_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EX-[AF]')


class FoodIMPQuestionExtractor(QuestionDataExtractor):

    prefix = 'FOODIMP'
    no_subtype = True

    number_of_scores = 16

    def get_value_keypaths(self):
        return [
            ('data.FOODIMP.answers.S1.answer', 'S1'),
            ('data.FOODIMP.answers.S2.answer', 'S2'),
            ('data.FOODIMP.answers.S3.answer', 'S3'),
            ('data.FOODIMP.answers.S4.answer', 'S4'),
            ('data.FOODIMP.answers.S5.answer', 'S5'),
            ('data.FOODIMP.answers.S6.answer', 'S6'),
            ('data.FOODIMP.answers.S7.answer', 'S7'),
            ('data.FOODIMP.answers.S8.answer', 'S8'),
            ('data.FOODIMP.answers.S9.answer', 'S9'),
            ('data.FOODIMP.answers.S10.answer', 'S10'),
            ('data.FOODIMP.answers.S11.answer', 'S11'),
            ('data.FOODIMP.answers.S12.answer', 'S12'),
            ('data.FOODIMP.answers.S13.answer', 'S13'),
            ('data.FOODIMP.answers.S14.answer', 'S14'),
            ('data.FOODIMP.answers.S15.answer', 'S15'),
            ('data.FOODIMP.answers.S16.answer', 'S16'),
            ('data.FOODIMP.timeOnQuestion', 'Time On Question'),
        ]

    def get_derived_value_keypaths(self):
        return [
            ('S1',  'S1 Score', self.code_response),
            ('S2',  'S2 Score', self.code_response),
            ('S3',  'S3 Score', self.code_response),
            ('S4',  'S4 Score', self.code_response),
            ('S5',  'S5 Score', self.code_response),
            ('S6',  'S6 Score', self.code_response),
            ('S7',  'S7 Score', self.code_response),
            ('S8',  'S8 Score', self.code_response_reversed),
            ('S9',  'S9 Score', self.code_response),
            ('S10', 'S10 Score', self.code_response_reversed),
            ('S11', 'S11 Score', self.code_response),
            ('S12', 'S12 Score', self.code_response_reversed),
            ('S13', 'S13 Score', self.code_response),
            ('S14', 'S14 Score', self.code_response_multiple),
            ('S15', 'S15 Score', self.code_response_multiple),
            ('S16', 'S16 Score', self.code_response_multiple),
            (None, 'Sum Scores', self.calculate_sum_scores),
            (None, 'Missing Scores', self.calculate_missing_scores),
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

    @staticmethod
    def code_response_multiple(response_value):
        coding_scheme = {
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
            ('data.GOALS.answers.ideal-weight.answer.unit1_val', 'Ideal Weight Unit 1 Value'),
            ('data.GOALS.answers.ideal-weight.answer.unit2_val', 'Ideal Weight Unit 2 Value'),
            ('data.GOALS.answers.ideal-weight.answer.units', 'Ideal Weight Units'),
            ('data.GOALS.answers.achievable-weight.answer.unit1_val', 'Achievable Weight Unit 1 Value'),
            ('data.GOALS.answers.achievable-weight.answer.unit2_val', 'Achievable Weight Unit 2 Value'),
            ('data.GOALS.answers.achievable-weight.answer.units', 'Achievable Weight Units'),
            ('data.GOALS.answers.happy-weight.answer.unit1_val', 'Happy Weight Unit 1 Value'),
            ('data.GOALS.answers.happy-weight.answer.unit2_val', 'Happy Weight Unit 2 Value'),
            ('data.GOALS.answers.happy-weight.answer.units', 'Happy Weight Units'),
            ('data.GOALS.timeOnQuestion', 'Time On Question'),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'GOALS')


class IntentQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'INTENT'
    no_subtype = True

    def get_value_keypaths(self):
        return [
            ('data.INTENT-H.answers.healthy-foods.answer', 'Healthy Foods Answer'),
            ('data.INTENT-H.timeOnQuestion', 'Healthy Foods Answer'),
            ('data.INTENT-U.answers.unhealthy-foods.answer', 'Unhealthy Foods Answer'),
            ('data.INTENT-U.timeOnQuestion', 'Unhealthy Foods Answer'),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'INTENT-[UH]')


class EffectQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'EFFECT'
    no_subtype = True

    def get_value_keypaths(self):
        return [
            ('data.EFFECT-H.answers.healthy.answer', 'H Answer'),
            ('data.EFFECT-H.timeOnQuestion', 'H Time on Question'),
            ('data.EFFECT-U.answers.unhealthy.answer', 'U Answer'),
            ('data.EFFECT-U.timeOnQuestion', 'U Time on Question'),
            ('data.EFFECT-W.answers.weight.answer', 'W Answer'),
            ('data.EFFECT-W.timeOnQuestion', 'W Time on Question'),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EFFECT-[HUW]')


class MINDFQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'MINDF'
    no_subtype = True

    number_of_scores = 15

    def get_value_keypaths(self):
        return [
            ('data.MINDF.answers.S1.answer', 'S1'),
            ('data.MINDF.answers.S2.answer', 'S2'),
            ('data.MINDF.answers.S3.answer', 'S3'),
            ('data.MINDF.answers.S4.answer', 'S4'),
            ('data.MINDF.answers.S5.answer', 'S5'),
            ('data.MINDF.answers.S6.answer', 'S6'),
            ('data.MINDF.answers.S7.answer', 'S7'),
            ('data.MINDF.answers.S8.answer', 'S8'),
            ('data.MINDF.answers.S9.answer', 'S9'),
            ('data.MINDF.answers.S10.answer', 'S10'),
            ('data.MINDF.answers.S11.answer', 'S11'),
            ('data.MINDF.answers.S12.answer', 'S12'),
            ('data.MINDF.answers.S13.answer', 'S13'),
            ('data.MINDF.answers.S14.answer', 'S14'),
            ('data.MINDF.answers.S15.answer', 'S15'),
            ('data.MINDF.timeOnQuestion', 'Time On Question'),
        ]

    def get_derived_value_keypaths(self):
        return [
            (None, 'Sum Scores', self.calculate_sum_scores),
            (None, 'Missing Scores', self.calculate_missing_scores),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MINDF')
