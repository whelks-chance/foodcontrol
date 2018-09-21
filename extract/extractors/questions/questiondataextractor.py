import re

# from utils import KeypathDict, irange
from utils import irange

from extractors.dataextractor import DataExtractor


class QuestionDataExtractor(DataExtractor):
    """The abstract base class for all questionnair data extractors"""

    type = 'tellusmore'

    def __init__(self):
        super().__init__()
        self.rows = []

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
            return super().get_value_keypaths()

    def can_process_row(self, row):
        return super().can_process_row(row) and self.can_process_data(row['data'])

    @staticmethod
    def can_process_data_with_pattern(data, pattern):
        data_keys = data.keys()
        for data_key in data_keys:
            if re.match(pattern, data_key):
                print('MATCH: {} == {}'.format(data_key, pattern))
                return True
        return False

    def extract_row_data(self, row):
        print('B:', row)
        values = self.extract_values(row)
        print('------>', values)

    # # TODO: now extract_row()
    # def extract_row(self, row):
    #     """
    #     The generic extraction routine for questions with a simple type,
    #     i.e. not a major minor or major character type
    #     """
    #     values = self.extract_values(row)
    #     print('------>', values)

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

    def extracted_rows(self):
        column_names = self.get_column_names()
        print('#######', self.rows)
        print(column_names)
        return [self.listify_values(column_names, row) for row in self.rows]


class EXQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'EX'

    def get_value_keypaths(self):
        return [
            ('EX-A.answers.0.answer', 'EX A Answer'),
            ('EX-A.timeOnQuestion', 'EX A Time On Question'),
            ('EX-F.answers.exercise-times-moderate.answer', 'EX F Times Moderate'),
            ('EX-F.answers.exercise-times-vigorous.answer', 'EX F Times Vigorous'),
            ('EX-F.answers.exercise-times-strengthening.answer', 'EX F Times Strengthening'),
            ('EX-F.answers.exercise-minutes-moderate.answer', 'EX F Minutes Moderate'),
            ('EX-F.answers.exercise-minutes-vigorous.answer', 'EX F Minutes Vigorous'),
            ('EX-F.answers.exercise-minutes-strengthening.answer', 'EX F Minutes Strengthening'),
        ]

    # TODO: Update
    derived_fields = [
        ('EX A Answer', 'EX A Answer Score', 'code_answer'),
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

    number_of_scores = 16

    def get_value_keypaths(self):
        return [
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

    # TODO: Update
    derived_fields = [
        ('S1',  'S1 Score', 'code_response'),
        ('S2',  'S2 Score', 'code_response'),
        ('S3',  'S3 Score', 'code_response'),
        ('S4',  'S4 Score', 'code_response'),
        ('S5',  'S5 Score', 'code_response'),
        ('S6',  'S6 Score', 'code_response'),
        ('S7',  'S7 Score', 'code_response'),
        ('S8',  'S8 Score', 'code_response_reversed'),
        ('S9',  'S9 Score', 'code_response'),
        ('S10', 'S10 Score', 'code_response_reversed'),
        ('S11', 'S11 Score', 'code_response'),
        ('S12', 'S12 Score', 'code_response_reversed'),
        ('S13', 'S13 Score', 'code_response'),
        ('S14', 'S14 Score', 'code_response_multiple'),
        ('S15', 'S15 Score', 'code_response_multiple'),
        ('S16', 'S16 Score', 'code_response_multiple'),
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

    def extract(self, data):
        super().extract(data, self.prefix)


class GoalsQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'GOALS'

    def get_value_keypaths(self):
        return [
            ('answers.ideal-weight.answer.unit1_val', 'Ideal Weight Unit 1 Value'),
            ('answers.ideal-weight.answer.unit2_val', 'Ideal Weight Unit 2 Value'),
            ('answers.ideal-weight.answer.units', 'Ideal Weight Units'),
            ('answers.achievable-weight.answer.unit1_val', 'Achievable Weight Unit 1 Value'),
            ('answers.achievable-weight.answer.unit2_val', 'Achievable Weight Unit 2 Value'),
            ('answers.achievable-weight.answer.units', 'Achievable Weight Units'),
            ('answers.happy-weight.answer.unit1_val', 'Happy Weight Unit 1 Value'),
            ('answers.happy-weight.answer.unit2_val', 'Happy Weight Unit 2 Value'),
            ('answers.happy-weight.answer.units', 'Happy Weight Units'),
            ('timeOnQuestion', 'Time On Question'),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'GOALS')

    def extract(self, data):
        super().extract(data, self.prefix)


class IntentQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'INTENT'

    def get_value_keypaths(self):
        return [
            ('INTENT-H.answers.healthy-foods.answer', 'Healthy Foods Answer'),
            ('INTENT-H.timeOnQuestion', 'Healthy Foods Answer'),
            ('INTENT-U.answers.unhealthy-foods.answer', 'Unhealthy Foods Answer'),
            ('INTENT-U.timeOnQuestion', 'Unhealthy Foods Answer'),
        ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'INTENT-[UH]')


class MINDFQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'MINDF'

    number_of_scores = 15

    def get_value_keypaths(self):
        return [
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
            ('timeOnQuestion', 'Time On Question'),
        ]

    # TODO: Update
    derived_fields = [
        (None, 'Sum Scores', 'calculate_sum_scores'),
        (None, 'Missing Scores', 'calculate_missing_scores'),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MINDF')

    def extract(self, data):
        print('EXTRACT', self.prefix)
        print(data)
        super().extract(data)
