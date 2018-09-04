import re
import pprint

pp = pprint.PrettyPrinter()

from .dataextractor import DataExtractor

from keypathdict import KeypathDict


def irange(start, end):
    """Return a range that includes the end value: 1,5 -> 1...5 rather than 1...4"""
    return range(start, end + 1)


class AbstractQuestionExtractor:

    rows = []

    def column_names(self):
        """Return a list of column names"""
        column_names = []
        for column_name, _, code in self.fields:
            column_names.append(column_name)
            if code:
                code_column_name, _ = code
                column_names.append(code_column_name)
        return column_names

    def can_process_data(self, data):
        # Create a pattern that matches a question prefix with major and minor numbers
        pattern = self.prefix + r'[12345]-1?\d'
        return self.can_process_data_with_pattern(data, pattern)

    @staticmethod
    def can_process_data_with_pattern(data, pattern):
        data_keys = data.keys()
        for data_key in data_keys:
            if re.match(pattern, data_key):
                return True
        return False

    def clear(self):
        """Reset common value and calculation stores. Override to to reset type-specific value and calculation stores"""
        self.rows = []

    def extract(self, data):
        """Store the column value for each keypath"""
        self.clear()
        self.extract_key_data(data)

    def extract_key_data(self, key_data):
        values = {}
        for column_name, keypath, code in self.fields:
            try:
                value = key_data.get_keypath_value(keypath)
                values[column_name] = value
                if code:
                    code_column_name, code_function_name = code
                    code_function = getattr(self, code_function_name)
                    code_value = DataExtractor.empty_cell_value
                    if value and value != DataExtractor.empty_cell_value:
                        code_value = code_function(value)
                    values[code_column_name] = code_value
            except KeyError as e:
                print('KeyError', e)
        self.calculate(values)
        self.rows.append(values)

    def calculate(self, values):
        # return values
        pass

class MajorMinorQuestionExtractor(AbstractQuestionExtractor):
    """
    A major minor question has a pattern of the form: FREQ1-1, FREQ1-2, FREQ1-3
    i.e. a question prefix, e.g. FREQ, TASTE and ATTRACT, followed by a major number
    in the range 1...n followed by a dash followed by a minor number in the range 1...m
    In the examples seen so far, n = 5 and m = 12
    """

    def extract(self, data):
        """Store the column value for each keypath"""
        self.clear()
        for major in self.major_range:
            for minor in self.minor_range:
                key = '{}{}-{}'.format(self.prefix, major, minor)
                try:
                    key_data = KeypathDict(data[key])
                    print(key, '->', key_data)
                    self.extract_key_data(key_data)
                except KeyError:
                    pass


class FreqExtractor(MajorMinorQuestionExtractor):

    prefix = 'FREQ'
    major_range = irange(1, 5)
    minor_range = irange(1, 12)

    fields = (
        ('TUM Session ID', 'TUMsessionID', None, ),
        ('FE', 'answers.FE.answer', ('FE Score', 'code_answer'), ),
        ('FC Answer', 'answers.FC.answer', ('FC Score', 'code_answer'), ),
        ('FC Slider Value', 'answers.FC.sliderValue', None, ),
        ('ID', 'VsmInfo.id', None, ),
        ('Type', 'VsmInfo.type', ('Type Value', 'code_food_type'), ),
        ('Selected', 'VsmInfo.selected', ('Selected Value', 'code_food_selected'), ),
        ('Time On Question', 'timeOnQuestion', None, ),
    )

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


class TasteExtractor(MajorMinorQuestionExtractor):

    prefix = 'TASTE'
    major_range = irange(1, 5)
    minor_range = irange(1, 12)

    fields = (
        ('TUM Session ID', 'TUMsessionID', None, ),
        ('FE', 'answers.0.answer', None, ),
        ('ID', 'VsmInfo.id', None, ),
        ('Type', 'VsmInfo.type', ('Type Value', 'code_food_type'), ),
        ('Selected', 'VsmInfo.selected', ('Selected Value', 'code_food_selected'), ),
        ('Time On Question', 'timeOnQuestion', None, ),
    )

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


class AttractExtractor(MajorMinorQuestionExtractor):

    prefix = 'ATTRACT'
    major_range = irange(1, 5)
    minor_range = irange(1, 12)

    fields = (
        ('TUM Session ID', 'TUMsessionID', None, ),
        ('FE', 'answers.0.answer', None, ),
        ('ID', 'VsmInfo.id', None, ),
        ('Type', 'VsmInfo.type', ('Type Value', 'code_food_type'), ),
        ('Selected', 'VsmInfo.selected', ('Selected Value', 'code_food_selected'), ),
        ('Time On Question', 'timeOnQuestion', None, ),
    )

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


class EXExtractor(AbstractQuestionExtractor):

    fields = (
        ('TUM Session ID', 'TUMsessionID', None, ),
        ('EX A Answer', 'EX-A.answers.0.answer', ('EX A Answer Score', 'code_answer'), ),
        ('EX A Time On Question', 'EX-A.timeOnQuestion', None, ),
        ('EX F Times Moderate', 'EX-F.answers.exercise-times-moderate.answer', None, ),
        ('EX F Times Vigorous', 'EX-F.answers.exercise-times-vigorous.answer', None, ),
        ('EX F Times Strengthening', 'EX-F.answers.exercise-times-strengthening.answer', None, ),
        ('EX F Minutes Moderate', 'EX-F.answers.exercise-minutes-moderate.answer', None, ),
        ('EX F Minutes Vigorous', 'EX-F.answers.exercise-minutes-vigorous.answer', None, ),
        ('EX F Minutes Strengthening', 'EX-F.answers.exercise-minutes-strengthening.answer', None, ),
    )

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EX-[AF]')

    @staticmethod
    def code_answer(answer_value):
        answer_codes = {
            'I am inactive':                   0,
            'My activity levels are low':      1,
            'My activity levels are moderate': 2,
        }
        return answer_codes[answer_value]


class WillExtractor(AbstractQuestionExtractor):

    fields = (
        ('TUM Session ID', 'TUMsessionID', None, ),

        ('S1', 'WILLM.answers.S1.answer', ('S1 Score', 'code_response_reversed'), ),
        ('S2', 'WILLM.answers.S2.answer', ('S2 Score', 'code_response_reversed'), ),
        ('S3', 'WILLM.answers.S3.answer', ('S3 Score', 'code_response'), ),
        ('S4', 'WILLM.answers.S4.answer', ('S4 Score', 'code_response'), ),
        ('S5', 'WILLM.answers.S5.answer', ('S5 Score', 'code_response_reversed'), ),
        ('S6', 'WILLM.answers.S6.answer', ('S6 Score', 'code_response'), ),

        ('S1', 'WILLT.answers.S1.answer', ('S1 Score', 'code_response_reversed'), ),
        ('S2', 'WILLT.answers.S2.answer', ('S2 Score', 'code_response_reversed'), ),
        ('S3', 'WILLT.answers.S3.answer', ('S3 Score', 'code_response'), ),
        ('S4', 'WILLT.answers.S4.answer', ('S4 Score', 'code_response_reversed'), ),
        ('S5', 'WILLT.answers.S5.answer', ('S5 Score', 'code_response'), ),
        ('S6', 'WILLT.answers.S6.answer', ('S6 Score', 'code_response'), ),
    )

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'WILL[MT]')

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

    def column_names(self):
        return super().column_names() + ['Scores Sum', 'Num Missing']

    def calculate(self, values):
        scores_sum = 0
        missing_sum = 0
        # Score 1, Score 2, ... , Score 6
        column_names = ['S' + str(response) + ' Score' for response in irange(1, 6)]
        for column_name in column_names:
            value = values[column_name]
            if value == DataExtractor.empty_cell_value:
                missing_sum += 1
            else:
                scores_sum += values[column_name]
        values['Scores Sum'] = scores_sum
        values['Num Missing'] = missing_sum
        # return values


class MoodExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MOOD[DAS]')


class IMPExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'IMP[AMN]')


class FoodIMPExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'FOODIMP')


class EMREGExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EMREG[NGIASC]')


class GoalsExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'GOALS')


class IntentExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'INTENT-[UH]')


class PersonExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'PERSON[NEOAC]')


class EffectExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EFFECT-[HUW]')


class MINDFExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MINDF')


class RESTRExtractor(AbstractQuestionExtractor):

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'RESTR')


class TellUsMoreDataExtractor(DataExtractor):

    type = 'tellusmore'

    rows = []
    question_extractor = None

    question_extractors = [
        FreqExtractor(),
        TasteExtractor(),
        AttractExtractor(),
        EXExtractor(),
        WillExtractor(),
        # MoodExtractor(),
        # IMPExtractor(),
        # FoodIMPExtractor(),
        # EMREGExtractor(),
        # GoalsExtractor(),
        # IntentExtractor(),
        # PersonExtractor(),
        # EffectExtractor(),
        # MINDFExtractor(),
        # RESTRExtractor(),
    ]

    def column_names(self):
        """Return a list of column names"""
        if self.question_extractor:
            return self.question_extractor.column_names()
        else:
            return []

    def get_question_extractor(self, data):
        for question_extractor in self.question_extractors:
            if question_extractor.can_process_data(data):
                return question_extractor
        return None

    def extract(self, row):
        self.rows = []
        data = KeypathDict(row['data'])
        question_extractor = self.get_question_extractor(data)
        if question_extractor:
            self.question_extractor = question_extractor
            self.question_extractor.extract(data)
            self.rows = self.question_extractor.rows
            print("self.rows:", self.rows)
        else:
            # TODO: Implement the remaining question extractors
            pass

    def check(self, row):
        pass

    def calculate(self, row):
        pass

    def extracted_rows(self):
        print('#######', self.rows)
        print(self.column_names())
        return [self.common_row_values() + self.to_list(self.column_names(), row) for row in self.rows]
