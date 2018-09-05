import re
import pprint

pp = pprint.PrettyPrinter()

from .dataextractor import DataExtractor

from keypathdict import KeypathDict


def irange(start, end):
    """Return a range that includes the end value: 1,5 -> 1...5 rather than 1...4"""
    return range(start, end + 1)


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

    def column_names(self):
        """Return a list of column names"""
        column_names = super().column_names()
        for _, derived_column_name, _ in self.derived_fields:
            column_names.append(derived_column_name)
        return column_names

    def can_process_row(self, row):
        """Return True if the row type matches the type this data extractor can process"""
        return row['type'] == self.__class__.type and self.can_process_data(row['data'])

    @staticmethod
    def can_process_data_with_pattern(data, pattern):
        data_keys = data.keys()
        for data_key in data_keys:
            if re.match(pattern, data_key):
                return True
        return False

    def extract(self, row):
        """Store the column value for each keypath"""
        self.clear()
        self.extract_key_data(row['data'])

    def extract_key_data(self, key_data):
        print('------------------------------------->QuestionExtractor.extract_key_data()')
        values = {}
        for column_name, keypath in self._fields():
            try:
                value = key_data.get_keypath_value(keypath)
                values[column_name] = value
                # if code:
                #     code_column_name, code_function_name = code
                #     code_function = getattr(self, code_function_name)
                #     code_value = DataExtractor.empty_cell_value
                #     if value and value != DataExtractor.empty_cell_value:
                #         code_value = code_function(value)
                #     values[code_column_name] = code_value
            except KeyError as e:
                print('KeyError', e)
        self.calculate(values)
        print('## VALUES:', self.values)

    def calculate(self, values):
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


class MajorMinorQuestionExtractor(QuestionExtractor):
    """
    A major minor question has a pattern of the form: FREQ1-1, FREQ1-2, FREQ1-3
    i.e. a question prefix, e.g. FREQ, TASTE and ATTRACT, followed by a major number
    in the range 1...n followed by a dash followed by a minor number in the range 1...m
    In the examples seen so far, n = 5 and m = 12
    """

    def extract(self, data):
        """Store the column value for each keypath"""
        self.clear()
        print('------------------------------------->MajorMinorQuestionExtractor.extract()')
        print(self.major_range, self.minor_range)
        print(data)
        data = data['data']
        for major in self.major_range:
            for minor in self.minor_range:
                key = '{}{}-{}'.format(self.prefix, major, minor)
                print(key)
                try:
                    key_data = KeypathDict(data[key])
                    print(key, '->', key_data)
                    self.extract_key_data(key_data)
                except KeyError:
                    pass

    def can_process_data(self, data):
        pattern = self.prefix + r'[12345]-1?\d'
        if self.can_process_data_with_pattern(data, pattern):
            print(self.prefix, '-->', data)
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


class EXQuestionExtractor(QuestionExtractor):

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

    def extract(self, data):
        """Store the column value for each keypath"""
        self.clear()
        for major in self.major_characters:
            key = '{}{}'.format(self.prefix, major)
            try:
                key_data = KeypathDict(data[key])
                print(key, '->', key_data)
                self.extract_key_data(key_data)
            except KeyError:
                pass


class WillQuestionExtractor(MajorCharacterQuestionExtractor):

    prefix = 'WILL'
    major_characters = ['M', 'T']

    fields = (
        # ('TUM Session ID', 'TUMsessionID', None, ),

        ('S1', 'answers.S1.answer', ('S1 Score', 'code_response_reversed'), ),
        ('S2', 'answers.S2.answer', ('S2 Score', 'code_response_reversed'), ),
        ('S3', 'answers.S3.answer', ('S3 Score', 'code_response'), ),
        ('S4', 'answers.S4.answer', ('S4 Score', 'code_response'), ),
        ('S5', 'answers.S5.answer', ('S5 Score', 'code_response_reversed'), ),
        ('S6', 'answers.S6.answer', ('S6 Score', 'code_response'), ),
    )

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

    fields = (
        # ('TUM Session ID', 'TUMsessionID', None, ),

        ( 'S1',  'answers.S1.answer', ( 'S1 Score', 'code_response'), ),
        ( 'S2',  'answers.S2.answer', ( 'S2 Score', 'code_response'), ),
        ( 'S3',  'answers.S3.answer', ( 'S3 Score', 'code_response'), ),
        ( 'S4',  'answers.S4.answer', ( 'S4 Score', 'code_response'), ),
        ( 'S5',  'answers.S5.answer', ( 'S5 Score', 'code_response'), ),
        ( 'S6',  'answers.S6.answer', ( 'S6 Score', 'code_response'), ),
        ( 'S7',  'answers.S7.answer', ( 'S7 Score', 'code_response'), ),
        ( 'S8',  'answers.S8.answer', ( 'S8 Score', 'code_response_reversed'), ),
        ( 'S9',  'answers.S9.answer', ( 'S9 Score', 'code_response'), ),
        ('S10', 'answers.S10.answer', ('S10 Score', 'code_response_reversed'), ),
        ('S11', 'answers.S11.answer', ('S11 Score', 'code_response'), ),
        ('S12', 'answers.S12.answer', ('S12 Score', 'code_response_reversed'), ),
        ('S13', 'answers.S13.answer', ('S13 Score', 'code_response'), ),
        ('S14', 'answers.S14.answer', ('S14 Score', 'code_response_reversed'), ),
        ('S15', 'answers.S15.answer', ('S15 Score', 'code_response_reversed'), ),
        ('S16', 'answers.S16.answer', ('S16 Score', 'code_response_reversed'), ),
        ('Time On Question', 'timeOnQuestion', None, ),
    )

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


class IMPQuestionExtractor(MajorCharacterQuestionExtractor):

    prefix = 'IMP'
    major_characters = ['A', 'M', 'N']

    fields = (
        # ('TUM Session ID', 'TUMsessionID', None, ),

        ('S1', 'answers.S1.answer', ('S1 Score', 'code_response'), ),
        ('S2', 'answers.S2.answer', ('S2 Score', 'code_response'), ),
        ('S3', 'answers.S3.answer', ('S3 Score', 'code_response'), ),
        ('S4', 'answers.S4.answer', ('S4 Score', 'code_response'), ),
        ('S5', 'answers.S5.answer', ('S5 Score', 'code_response'), ),
        ('S6', 'answers.S6.answer', ('S6 Score', 'code_response'), ),
        ('S7', 'answers.S7.answer', ('S7 Score', 'code_response'), ),
        ('Time On Question', 'MOODD.timeOnQuestion', None, ),
    )

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

    fields = (
        # ('TUM Session ID', 'TUMsessionID', None, ),

        ( 'S1',  'answers.S1.answer', ( 'S1 Score', 'code_response'), ),
        ( 'S2',  'answers.S2.answer', ( 'S2 Score', 'code_response'), ),
        ( 'S3',  'answers.S3.answer', ( 'S3 Score', 'code_response'), ),
        ( 'S4',  'answers.S4.answer', ( 'S4 Score', 'code_response'), ),
        ( 'S5',  'answers.S5.answer', ( 'S5 Score', 'code_response'), ),
        ( 'S6',  'answers.S6.answer', ( 'S6 Score', 'code_response'), ),
        ( 'S7',  'answers.S7.answer', ( 'S7 Score', 'code_response'), ),
        ( 'S8',  'answers.S8.answer', ( 'S8 Score', 'code_response_reversed'), ),
        ( 'S9',  'answers.S9.answer', ( 'S9 Score', 'code_response'), ),
        ('S10', 'answers.S10.answer', ('S10 Score', 'code_response_reversed'), ),
        ('S11', 'answers.S11.answer', ('S11 Score', 'code_response'), ),
        ('S12', 'answers.S12.answer', ('S12 Score', 'code_response_reversed'), ),
        ('S13', 'answers.S13.answer', ('S13 Score', 'code_response'), ),
        ('S14', 'answers.S14.answer', ('S14 Score', 'code_response_multiple'), ),
        ('S15', 'answers.S15.answer', ('S15 Score', 'code_response_multiple'), ),
        ('S16', 'answers.S16.answer', ('S16 Score', 'code_response_multiple'), ),
        ('Time On Question', 'timeOnQuestion', None, ),
    )

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


class EMREGExtractor(MajorCharacterQuestionExtractor):

    prefix = 'EMREG'
    major_characters = ['N', 'G', 'I', 'A', 'S', 'C']

    fields = (
        ('S1', 'answers.S1.answer', None, ),
        ('S2', 'answers.S2.answer', None, ),
        ('S3', 'answers.S3.answer', None, ),
        ('S4', 'answers.S4.answer', None, ),
        ('S5', 'answers.S5.answer', None, ),
        ('S6', 'answers.S6.answer', None, ),
        ('S7', 'answers.S7.answer', None, ),
        ('S8', 'answers.S8.answer', None, ),
        ('Time on Question', 'timeOnQuestion', None, ),
    )

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

    fields = (
        ('Ideal Weight Unit 1 Value', 'answers.ideal-weight.answer.unit1_val', None, ),
        ('Ideal Weight Unit 2 Value', 'answers.ideal-weight.answer.unit2_val', None, ),
        ('Ideal Weight Units', 'answers.ideal-weight.answer.units', None, ),
        ('Achievable Weight Unit 1 Value', 'answers.achievable-weight.answer.unit1_val', None, ),
        ('Achievable Weight Unit 2 Value', 'answers.achievable-weight.answer.unit2_val', None, ),
        ('Achievable Weight Units', 'answers.achievable-weight.answer.units', None, ),
        ('Happy Weight Unit 1 Value', 'answers.happy-weight.answer.unit1_val', None, ),
        ('Happy Weight Unit 2 Value', 'answers.happy-weight.answer.unit2_val', None, ),
        ('Happy Weight Units', 'answers.happy-weight.answer.units', None, ),
        ('Time On Question', 'timeOnQuestion', None, ),
    )

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'GOALS')

    def extract(self, data):
        """Store the column value for each keypath"""
        self.clear()
        key = 'GOALS'
        key_data = KeypathDict(data[key])
        print(key, '->', key_data)
        self.extract_key_data(key_data)


class IntentQuestionExtractor(QuestionExtractor):

    fields = (
        ('Healthy Foods Answer', 'INTENT-H.answers.healthy-foods.answer', None, ),
        ('Healthy Foods Answer', 'INTENT-H.timeOnQuestion', None, ),
        ('Unhealthy Foods Answer', 'INTENT-U.answers.unhealthy-foods.answer', None, ),
        ('Unhealthy Foods Answer', 'INTENT-U.timeOnQuestion', None, ),
    )

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'INTENT-[UH]')


class PersonQuestionExtractor(MajorCharacterQuestionExtractor):

    prefix = 'PERSON'
    major_characters = ['N', 'E', 'O', 'A', 'C']

    fields = (
        ( 'S1', 'answers.S1.answer',  ('S1 Score',  'code_response'), ),
        ( 'S2', 'answers.S2.answer',  ('S2 Score',  'code_response'), ),
        ( 'S3', 'answers.S3.answer',  ('S3 Score',  'code_response'), ),
        ( 'S4', 'answers.S4.answer',  ('S4 Score',  'code_response'), ),
        ( 'S5', 'answers.S5.answer',  ('S5 Score',  'code_response'), ),
        ( 'S6', 'answers.S6.answer',  ('S6 Score',  'code_response_reversed'), ),
        ( 'S7', 'answers.S7.answer',  ('S7 Score',  'code_response_reversed'), ),
        ( 'S8', 'answers.S8.answer',  ('S8 Score',  'code_response_reversed'), ),
        ( 'S9', 'answers.S9.answer',  ('S9 Score',  'code_response_reversed'), ),
        ('S10', 'answers.S10.answer', ('S10 Score', 'code_response_reversed'), ),
        ('Time On Question', 'timeOnQuestion', None,),
    )

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

    fields = (
        ('H Answer', 'EFFECT-H.answers.healthy.answer', None, ),
        ('H Time on Question', 'EFFECT-H.timeOnQuestion', None, ),
        ('U Answer', 'EFFECT-U.answers.unhealthy.answer', None, ),
        ('U Time on Question', 'EFFECT-U.timeOnQuestion', None, ),
        ('W Answer', 'EFFECT-W.answers.weight.answer', None, ),
        ('W Time on Question', 'EFFECT-W.timeOnQuestion', None, ),
    )

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'EFFECT-[HUW]')


class MINDFQuestionExtractor(QuestionExtractor):

    fields = (
        ( 'S1', 'answers.S1.answer',  None, ),
        ( 'S2', 'answers.S2.answer',  None, ),
        ( 'S3', 'answers.S3.answer',  None, ),
        ( 'S4', 'answers.S4.answer',  None, ),
        ( 'S5', 'answers.S5.answer',  None, ),
        ( 'S6', 'answers.S6.answer',  None, ),
        ( 'S7', 'answers.S7.answer',  None, ),
        ( 'S8', 'answers.S8.answer',  None, ),
        ( 'S9', 'answers.S9.answer',  None, ),
        ('S10', 'answers.S10.answer', None, ),
        ('S11', 'answers.S11.answer', None, ),
        ('S12', 'answers.S12.answer', None, ),
        ('S13', 'answers.S13.answer', None, ),
        ('S14', 'answers.S14.answer', None, ),
        ('S15', 'answers.S15.answer', None, ),
        ('Time On Question', 'timeOnQuestion', None,),
    )

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'MINDF')

    def calculate(self, values):
        self.calculate_sum_and_missing_scores(values, number_of_scores=15)


class RESTRQuestionExtractor(MajorCharacterQuestionExtractor):

    prefix = 'RESTR-'
    major_characters = ['C', 'W']

    fields = (
        ('S1', 'answers.S1.answer', None, ),
        ('S2', 'answers.S2.answer', None, ),
        ('S3', 'answers.S3.answer', None, ),
        ('S4', 'answers.S4.answer', None, ),
        ('S5', 'answers.S5.answer', None, ),
        ('S6', 'answers.S6.answer', None, ),
        ('Time on Question', 'timeOnQuestion', None, ),
    )

    def can_process_data(self, data):
        return self.can_process_data_with_pattern(data, r'RESTR-[CW]')

    def calculate(self, values):
        self.calculate_sum_and_missing_scores(values, number_of_scores=16)


class TellUsMoreDataExtractor(DataExtractor):

    type = 'tellusmore'

    rows = []
    question_extractor = None

    question_extractors = [
        FreqQuestionExtractor(),
        TasteQuestionExtractor(),
        AttractQuestionExtractor(),
        EXQuestionExtractor(),
        WillQuestionExtractor(),
        MoodQuestionExtractor(),
        IMPQuestionExtractor(),
        FoodIMPQuestionExtractor(),
        # EMREGExtractor(),
        GoalsQuestionExtractor(),
        IntentQuestionExtractor(),
        PersonQuestionExtractor(),
        EffectQuestionExtractor(),
        MINDFQuestionExtractor(),
        RESTRQuestionExtractor(),
    ]

    def column_names(self):
        """Return a list of column names"""
        if self.question_extractor:
            return ['Type'] + self.question_extractor.column_names()
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
