import re

from utils import KeypathDict, irange

from extractors.dataextractor import DataExtractor


class QuestionDataExtractor(DataExtractor):

    type = 'tellusmore'

    rows = []

    def name(self):
        return '{}-{}'.format(self.type, self.prefix)

    def common_fields(self):
        return super().common_fields() + [
            ('TUM Session ID', 'data.TUMsessionID', ),
        ]

    def can_process_row(self, row):
        """Return True if the row type matches the type this data extractor can process"""
        return super().can_process_row(row) and self.can_process_data(row['data'])

    @staticmethod
    def can_process_data_with_pattern(data, pattern):
        data_keys = data.keys()
        for data_key in data_keys:
            if re.match(pattern, data_key):
                return True
        return False

    def clear(self):
        pass

    def extract(self, row, data_key=None):
        """
        The generic extraction routine for questions with a simple type,
        i.e. not a major minor or major character type
        """
        values = {}
        self.rows = []
        data = KeypathDict(row['data'])
        if data_key:
            print('QQQQQQQQQQQQQQQQ', data_key, data)
            data = KeypathDict(data[data_key])
        else:
            print('QQQQQQQQQQQQQQQQ', data)
        self.extract_field_values(self._fields(), data, values)
        self.calculate_derived_field_values(values)
        print("WITH DERIVED: ", values)
        self.rows.append(values)

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
            if value == DataExtractor.empty_cell_value or value is None:
                missing_sum += 1
            else:
                print('column_name:', column_name)
                print('      value:', values[column_name])
                scores_sum += int(values[column_name])
        values['Scores Sum'] = scores_sum
        values['Num Missing'] = missing_sum

    def extracted_rows(self):
        print('#######', self.rows)
        print(self.column_names())
        return [self.common_row_values() + self.to_list(self.column_names(), row) for row in self.rows]

    @staticmethod
    def sum_scores(values):
        return -1

    @staticmethod
    def missing_scores(values):
        return -1


class EXQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'EX'

    fields = [
        ('EX A Answer', 'EX-A.answers.0.answer'),
        ('EX A Time On Question', 'EX-A.timeOnQuestion'),
        ('EX F Times Moderate', 'EX-F.answers.exercise-times-moderate.answer'),
        ('EX F Times Vigorous', 'EX-F.answers.exercise-times-vigorous.answer'),
        ('EX F Times Strengthening', 'EX-F.answers.exercise-times-strengthening.answer'),
        ('EX F Minutes Moderate', 'EX-F.answers.exercise-minutes-moderate.answer'),
        ('EX F Minutes Vigorous', 'EX-F.answers.exercise-minutes-vigorous.answer'),
        ('EX F Minutes Strengthening', 'EX-F.answers.exercise-minutes-strengthening.answer'),
    ]

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
        ('S11', 'answers.S11.answer'),
        ('S12', 'answers.S12.answer'),
        ('S13', 'answers.S13.answer'),
        ('S14', 'answers.S14.answer'),
        ('S15', 'answers.S15.answer'),
        ('S16', 'answers.S16.answer'),
        ('Time On Question', 'timeOnQuestion'),
    ]

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
        (None, 'Sum Scores', 'sum_scores'),
        (None, 'Missing Scores', 'missing_scores'),
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

    fields = [
        ('Ideal Weight Unit 1 Value', 'answers.ideal-weight.answer.unit1_val'),
        ('Ideal Weight Unit 2 Value', 'answers.ideal-weight.answer.unit2_val'),
        ('Ideal Weight Units', 'answers.ideal-weight.answer.units'),
        ('Achievable Weight Unit 1 Value', 'answers.achievable-weight.answer.unit1_val'),
        ('Achievable Weight Unit 2 Value', 'answers.achievable-weight.answer.unit2_val'),
        ('Achievable Weight Units', 'answers.achievable-weight.answer.units'),
        ('Happy Weight Unit 1 Value', 'answers.happy-weight.answer.unit1_val'),
        ('Happy Weight Unit 2 Value', 'answers.happy-weight.answer.unit2_val'),
        ('Happy Weight Units', 'answers.happy-weight.answer.units'),
        ('Time On Question', 'timeOnQuestion'),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'GOALS')

    def extract(self, data):
        super().extract(data, self.prefix)


class IntentQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'INTENT'

    fields = [
        ('Healthy Foods Answer', 'INTENT-H.answers.healthy-foods.answer'),
        ('Healthy Foods Answer', 'INTENT-H.timeOnQuestion'),
        ('Unhealthy Foods Answer', 'INTENT-U.answers.unhealthy-foods.answer'),
        ('Unhealthy Foods Answer', 'INTENT-U.timeOnQuestion'),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'INTENT-[UH]')


class MINDFQuestionDataExtractor(QuestionDataExtractor):

    prefix = 'MINDF'

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
        ('S11', 'answers.S11.answer'),
        ('S12', 'answers.S12.answer'),
        ('S13', 'answers.S13.answer'),
        ('S14', 'answers.S14.answer'),
        ('S15', 'answers.S15.answer'),
        ('Time On Question', 'timeOnQuestion'),
    ]

    derived_fields = [
        (None, 'Sum Scores', 'sum_scores'),
        (None, 'Missing Scores', 'missing_scores'),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MINDF')

    def extract(self, data):
        print('EXTRACT', self.prefix)
        super().extract(data, self.prefix)
