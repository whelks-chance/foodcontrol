import re

from utils import KeypathDict, irange
from .dataextractor import DataExtractor


class QuestionExtractor(DataExtractor):

    type = 'tellusmore'

    rows = []

    def name(self):
        return '{}-{}'.format(self.type, self.prefix)

    def common_fields(self):
        print('QuestionExtractor.common_fields()')
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


class MajorMinorQuestionExtractor(QuestionExtractor):
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


class FreqQuestionExtractor(MajorMinorQuestionExtractor):

    prefix = 'FREQ'
    major_range = irange(1, 5)
    minor_range = irange(1, 12)

    fields = [
        ('FE', 'answers.FE.answer', ),
        ('FC Answer', 'answers.FC.answer', ),
        ('FC Slider Value', 'answers.FC.sliderValue', ),
        ('ID', 'VsmInfo.id', ),
        ('Type', 'VsmInfo.type', ),
        ('Selected', 'VsmInfo.selected', ),
        ('Time On Question', 'timeOnQuestion', ),
    ]

    derived_fields = [
        ('FE', 'FE Score', 'code_answer', ),
        ('FC Answer', 'FC Score', 'code_answer', ),
        ('Type', 'Type Value', 'code_food_type'),
        ('Selected', 'Selected Value', 'code_food_selected', ),
    ]

    @staticmethod
    def code_food_type(food_value):
        food_type_codes = {
            'U': 0,
            'H': 1,
        }
        return food_type_codes[food_value]

    @staticmethod
    def code_food_selected(food_selected_value):
        food_selected_codes = {
            'Selected': 1,
            'MB':       2,
            'upload':   3,
            'random':   4,
            'add':      5,
        }
        return food_selected_codes[food_selected_value]

    @staticmethod
    def code_answer(answer_value):
        answer_codes = {
            'None':      0,
            '1-2 times': 1,
            '3-4 times': 2,
            '5-6 times': 3,
            '7+ times':  4,
        }
        return answer_codes[answer_value]


class TasteQuestionExtractor(MajorMinorQuestionExtractor):

    prefix = 'TASTE'
    major_range = irange(1, 5)
    minor_range = irange(1, 12)

    fields = [
        ('FE', 'answers.0.answer', ),
        ('ID', 'VsmInfo.id', ),
        ('Type', 'VsmInfo.type', ),
        ('Selected', 'VsmInfo.selected', ),
        ('Time On Question', 'timeOnQuestion', ),
    ]

    derived_fields = [
        ('Type', 'Type Value', 'code_food_type', ),
        ('Selected', 'Selected Value', 'code_food_selected', ),
    ]

    @staticmethod
    def code_food_type(food_value):
        food_type_codes = {
            'U': 0,
            'H': 1,
        }
        return food_type_codes[food_value]

    @staticmethod
    def code_food_selected(food_selected_value):
        food_selected_codes = {
            'Selected': 1,
            'MB':       2,
            'upload':   3,
            'random':   4,
            'add':      5,
        }
        return food_selected_codes[food_selected_value]


class AttractQuestionExtractor(MajorMinorQuestionExtractor):

    prefix = 'ATTRACT'
    major_range = irange(1, 5)
    minor_range = irange(1, 12)

    fields = [
        ('FE', 'answers.0.answer', ),
        ('ID', 'VsmInfo.id', ),
        ('Type', 'VsmInfo.type', ),
        ('Selected', 'VsmInfo.selected', ),
        ('Time On Question', 'timeOnQuestion', ),
    ]

    derived_fields = [
        ('Type', 'Type Value', 'code_food_type', ),
        ('Selected', 'Selected Value', 'code_food_selected', ),
    ]

    @staticmethod
    def code_food_type(food_value):
        food_type_codes = {
            'U': 0,
            'H': 1,
        }
        return food_type_codes[food_value]

    @staticmethod
    def code_food_selected(food_selected_value):
        food_selected_codes = {
            'Selected': 1,
            'MB':       2,
            'upload':   3,
            'random':   4,
            'add':      5,
        }
        return food_selected_codes[food_selected_value]


class EXQuestionExtractor(QuestionExtractor):

    prefix = 'EX'

    fields = [
        ('EX A Answer', 'EX-A.answers.0.answer', ),
        ('EX A Time On Question', 'EX-A.timeOnQuestion', ),
        ('EX F Times Moderate', 'EX-F.answers.exercise-times-moderate.answer', ),
        ('EX F Times Vigorous', 'EX-F.answers.exercise-times-vigorous.answer', ),
        ('EX F Times Strengthening', 'EX-F.answers.exercise-times-strengthening.answer', ),
        ('EX F Minutes Moderate', 'EX-F.answers.exercise-minutes-moderate.answer', ),
        ('EX F Minutes Vigorous', 'EX-F.answers.exercise-minutes-vigorous.answer', ),
        ('EX F Minutes Strengthening', 'EX-F.answers.exercise-minutes-strengthening.answer', ),
    ]

    derived_fields = [
        ('EX A Answer', 'EX A Answer Score', 'code_answer', ),
    ]

    @staticmethod
    def code_answer(answer_value):
        answer_codes = {
            'I am inactive':                   0,
            'My activity levels are low':      1,
            'My activity levels are moderate': 2,
        }
        return answer_codes[answer_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EX-[AF]')


class MajorCharacterQuestionExtractor(QuestionExtractor):
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


class WillQuestionExtractor(MajorCharacterQuestionExtractor):

    prefix = 'WILL'
    major_characters = ['M', 'T']

    fields = [
        ('S1', 'answers.S1.answer', ),
        ('S2', 'answers.S2.answer', ),
        ('S3', 'answers.S3.answer', ),
        ('S4', 'answers.S4.answer', ),
        ('S5', 'answers.S5.answer', ),
        ('S6', 'answers.S6.answer', ),
    ]

    derived_fields = [
        ('S1', 'S1 Score', 'code_response_reversed'),
        ('S2', 'S2 Score', 'code_response_reversed'),
        ('S3', 'S3 Score', 'code_response'),
        ('S4', 'S4 Score', 'code_response'),
        ('S5', 'S5 Score', 'code_response_reversed'),
        ('S6', 'S6 Score', 'code_response'),
    ]

    @staticmethod
    def code_response(response_value):
        response_codes = {
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
        }
        return response_codes[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        reversed_response_codes = {
            '1': 6,
            '2': 5,
            '3': 4,
            '4': 3,
            '5': 2,
            '6': 1,
        }
        return reversed_response_codes[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'WILL[MT]')

    def column_names(self):
        return super().column_names() + ['Scores Sum', 'Num Missing']

    def calculate(self, values):
        self.calculate_sum_and_missing_scores(values, number_of_scores=6)


class MoodQuestionExtractor(MajorCharacterQuestionExtractor):

    prefix = 'MOOD'
    major_characters = ['D', 'A', 'S']

    fields = [
        ('S1',  'answers.S1.answer', ),
        ('S2',  'answers.S2.answer', ),
        ('S3',  'answers.S3.answer', ),
        ('S4',  'answers.S4.answer', ),
        ('S5',  'answers.S5.answer', ),
        ('S6',  'answers.S6.answer', ),
        ('S7',  'answers.S7.answer', ),
        ('S8',  'answers.S8.answer', ),
        ('S9',  'answers.S9.answer', ),
        ('S10', 'answers.S10.answer', ),
        ('S11', 'answers.S11.answer', ),
        ('S12', 'answers.S12.answer', ),
        ('S13', 'answers.S13.answer', ),
        ('S14', 'answers.S14.answer', ),
        ('S15', 'answers.S15.answer', ),
        ('S16', 'answers.S16.answer', ),
        ('Time On Question', 'timeOnQuestion', ),
    ]

    derived_fields = [
        ('S1', 'S1 Score', 'code_response', ),
        ('S2', 'S2 Score', 'code_response', ),
        ('S3', 'S3 Score', 'code_response', ),
        ('S4', 'S4 Score', 'code_response', ),
        ('S5', 'S5 Score', 'code_response', ),
        ('S6', 'S6 Score', 'code_response', ),
        ('S7', 'S7 Score', 'code_response', ),
        ('S8', 'S8 Score', 'code_response_reversed', ),
        ('S9', 'S9 Score', 'code_response', ),
        ('S10', 'S10 Score', 'code_response_reversed', ),
        ('S11', 'S11 Score', 'code_response', ),
        ('S12', 'S12 Score', 'code_response_reversed', ),
        ('S13', 'S13 Score', 'code_response', ),
        ('S14', 'S14 Score', 'code_response_reversed', ),
        ('S15', 'S15 Score', 'code_response_reversed', ),
        ('S16', 'S16 Score', 'code_response_reversed', ),
    ]

    @staticmethod
    def code_response(response_value):
        response_codes = {
            '1': 1,
            '0': 0,
        }
        return response_codes[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        reversed_response_codes = {
            '1': 0,
            '0': 1,
        }
        return reversed_response_codes[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MOOD[DAS]')

    def column_names(self):
        return super().column_names() + ['Scores Sum', 'Num Missing']

    def calculate(self, values):
        self.calculate_sum_and_missing_scores(values, number_of_scores=7)


# TODO: Handle different scoring systems for different major characters
class IMPQuestionExtractor(MajorCharacterQuestionExtractor):

    prefix = 'IMP'
    major_characters = ['A', 'M', 'N']

    fields = [
        ('S1', 'answers.S1.answer', ),
        ('S2', 'answers.S2.answer', ),
        ('S3', 'answers.S3.answer', ),
        ('S4', 'answers.S4.answer', ),
        ('S5', 'answers.S5.answer', ),
        ('S6', 'answers.S6.answer', ),
        ('S7', 'answers.S7.answer', ),
        ('Time On Question', 'MOODD.timeOnQuestion', None, ),
    ]

    derived_fields = [
        ('S1', 'S1 Score', 'code_response'),
        ('S2', 'S2 Score', 'code_response'),
        ('S3', 'S3 Score', 'code_response'),
        ('S4', 'S4 Score', 'code_response'),
        ('S5', 'S5 Score', 'code_response'),
        ('S6', 'S6 Score', 'code_response'),
        ('S7', 'S7 Score', 'code_response'),
    ]

    @staticmethod
    def code_response(response_value):
        response_codes = {
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
        }
        return response_codes[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        reversed_response_codes = {
            '1': 4,
            '2': 3,
            '3': 2,
            '4': 1,
        }
        return reversed_response_codes[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'IMP[AMN]')


class FoodIMPQuestionExtractor(QuestionExtractor):

    prefix = 'FOODIMP'

    fields = [
        ('S1', 'answers.S1.answer', ),
        ('S2', 'answers.S2.answer', ),
        ('S3', 'answers.S3.answer', ),
        ('S4', 'answers.S4.answer', ),
        ('S5', 'answers.S5.answer', ),
        ('S6', 'answers.S6.answer', ),
        ('S7', 'answers.S7.answer', ),
        ('S8', 'answers.S8.answer', ),
        ('S9', 'answers.S9.answer', ),
        ('S10', 'answers.S10.answer', ),
        ('S11', 'answers.S11.answer', ),
        ('S12', 'answers.S12.answer', ),
        ('S13', 'answers.S13.answer', ),
        ('S14', 'answers.S14.answer', ),
        ('S15', 'answers.S15.answer', ),
        ('S16', 'answers.S16.answer', ),
        ('Time On Question', 'timeOnQuestion', ),
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
    ]

    @staticmethod
    def code_response(response_value):
        response_codes = {
            '1': 1,
            '0': 0,
        }
        return response_codes[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        reversed_response_codes = {
            '1': 0,
            '0': 1,
        }
        return reversed_response_codes[response_value]

    @staticmethod
    def code_response_multiple(response_value):
        multiple_response_codes = {
            '0': 0,
            '1': 0,
            '2': 1,
            '3': 1,
        }
        return multiple_response_codes[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'FOODIMP')


class EMREGQuestionExtractor(MajorCharacterQuestionExtractor):

    prefix = 'EMREG'
    major_characters = ['N', 'G', 'I', 'A', 'S', 'C']

    fields = [
        ('S1', 'answers.S1.answer', ),
        ('S2', 'answers.S2.answer', ),
        ('S3', 'answers.S3.answer', ),
        ('S4', 'answers.S4.answer', ),
        ('S5', 'answers.S5.answer', ),
        ('S6', 'answers.S6.answer', ),
        ('S7', 'answers.S7.answer', ),
        ('S8', 'answers.S8.answer', ),
        ('Time on Question', 'timeOnQuestion', ),
    ]

    derived_fields = [
        ('S1', 'S1 Score', 'code_response', ),
        ('S2', 'S2 Score', 'code_response', ),
        ('S3', 'S3 Score', 'code_response', ),
        ('S4', 'S4 Score', 'code_response', ),
        ('S5', 'S5 Score', 'code_response', ),
        ('S6', 'S6 Score', 'code_response', ),
        ('S7', 'S7 Score', 'code_response', ),
        ('S8', 'S8 Score', 'code_response', ),
    ]

    @staticmethod
    def code_response(response_value):
        response_codes = {
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
        }
        return response_codes[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        reversed_response_codes = {
            '1': 5,
            '2': 4,
            '3': 3,
            '4': 2,
            '5': 1,
        }
        return reversed_response_codes[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EMREG[NGIASC]')

    def calculate(self, values):
        # self.calculate_sum_and_missing_scores(values, number_of_scores=15)
        pass


class GoalsQuestionExtractor(QuestionExtractor):

    prefix = 'GOALS'

    fields = [
        ('Ideal Weight Unit 1 Value', 'answers.ideal-weight.answer.unit1_val', ),
        ('Ideal Weight Unit 2 Value', 'answers.ideal-weight.answer.unit2_val', ),
        ('Ideal Weight Units', 'answers.ideal-weight.answer.units', ),
        ('Achievable Weight Unit 1 Value', 'answers.achievable-weight.answer.unit1_val', ),
        ('Achievable Weight Unit 2 Value', 'answers.achievable-weight.answer.unit2_val', ),
        ('Achievable Weight Units', 'answers.achievable-weight.answer.units', ),
        ('Happy Weight Unit 1 Value', 'answers.happy-weight.answer.unit1_val', ),
        ('Happy Weight Unit 2 Value', 'answers.happy-weight.answer.unit2_val', ),
        ('Happy Weight Units', 'answers.happy-weight.answer.units', ),
        ('Time On Question', 'timeOnQuestion', ),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'GOALS')

    def extract(self, data):
        super().extract(data, self.prefix)


class IntentQuestionExtractor(QuestionExtractor):

    prefix = 'INTENT'

    fields = [
        ('Healthy Foods Answer', 'INTENT-H.answers.healthy-foods.answer', ),
        ('Healthy Foods Answer', 'INTENT-H.timeOnQuestion', ),
        ('Unhealthy Foods Answer', 'INTENT-U.answers.unhealthy-foods.answer', ),
        ('Unhealthy Foods Answer', 'INTENT-U.timeOnQuestion', ),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'INTENT-[UH]')


class PersonQuestionExtractor(MajorCharacterQuestionExtractor):

    prefix = 'PERSON'
    major_characters = ['N', 'E', 'O', 'A', 'C']

    fields = [
        ('S1', 'answers.S1.answer', ),
        ('S2', 'answers.S2.answer', ),
        ('S3', 'answers.S3.answer', ),
        ('S4', 'answers.S4.answer', ),
        ('S5', 'answers.S5.answer', ),
        ('S6', 'answers.S6.answer', ),
        ('S7', 'answers.S7.answer', ),
        ('S8', 'answers.S8.answer', ),
        ('S9', 'answers.S9.answer', ),
        ('S10', 'answers.S10.answer', ),
        ('Time On Question', 'timeOnQuestion', ),
    ]

    derived_fields = [
        ('S1', 'S1 Score', 'code_response', ),
        ('S2', 'S2 Score', 'code_response', ),
        ('S3', 'S3 Score', 'code_response', ),
        ('S4', 'S4 Score', 'code_response', ),
        ('S5', 'S5 Score', 'code_response', ),
        ('S6', 'S6 Score', 'code_response', ),
        ('S7', 'S7 Score', 'code_response', ),
        ('S8', 'S8 Score', 'code_response', ),
        ('S9', 'S6 Score', 'code_response', ),
        ('S10', 'S7 Score', 'code_response', ),
    ]

    @staticmethod
    def code_response(response_value):
        response_codes = {
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
        }
        return response_codes[response_value]

    @staticmethod
    def code_response_reversed(response_value):
        reversed_response_codes = {
            '1': 5,
            '2': 4,
            '3': 3,
            '4': 2,
            '5': 1,
        }
        return reversed_response_codes[response_value]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'PERSON[NEOAC]')


class EffectQuestionExtractor(QuestionExtractor):

    prefix = 'EFFECT'

    fields = [
        ('H Answer', 'EFFECT-H.answers.healthy.answer', ),
        ('H Time on Question', 'EFFECT-H.timeOnQuestion', ),
        ('U Answer', 'EFFECT-U.answers.unhealthy.answer', ),
        ('U Time on Question', 'EFFECT-U.timeOnQuestion', ),
        ('W Answer', 'EFFECT-W.answers.weight.answer', ),
        ('W Time on Question', 'EFFECT-W.timeOnQuestion', ),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EFFECT-[HUW]')


class MINDFQuestionExtractor(QuestionExtractor):

    prefix = 'MINDF'

    fields = [
        ('S1', 'answers.S1.answer', ),
        ('S2', 'answers.S2.answer', ),
        ('S3', 'answers.S3.answer', ),
        ('S4', 'answers.S4.answer', ),
        ('S5', 'answers.S5.answer', ),
        ('S6', 'answers.S6.answer', ),
        ('S7', 'answers.S7.answer', ),
        ('S8', 'answers.S8.answer', ),
        ('S9', 'answers.S9.answer', ),
        ('S10', 'answers.S10.answer', ),
        ('S11', 'answers.S11.answer', ),
        ('S12', 'answers.S12.answer', ),
        ('S13', 'answers.S13.answer', ),
        ('S14', 'answers.S14.answer', ),
        ('S15', 'answers.S15.answer', ),
        ('Time On Question', 'timeOnQuestion', ),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MINDF')

    def extract(self, data):
        print('EXTRACT', self.prefix)
        super().extract(data, self.prefix)

    def calculate(self, values):
        self.calculate_sum_and_missing_scores(values, number_of_scores=15)


class RESTRQuestionExtractor(MajorCharacterQuestionExtractor):

    prefix = 'RESTR-'
    major_characters = ['C', 'W']

    fields = [
        ('S1', 'answers.S1.answer', ),
        ('S2', 'answers.S2.answer', ),
        ('S3', 'answers.S3.answer', ),
        ('S4', 'answers.S4.answer', ),
        ('S5', 'answers.S5.answer', ),
        ('S6', 'answers.S6.answer', ),
        ('Time on Question', 'timeOnQuestion', ),
    ]

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'RESTR-[CW]')

    def calculate(self, values):
        self.calculate_sum_and_missing_scores(values, number_of_scores=16)
