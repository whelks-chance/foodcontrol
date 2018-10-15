from .gamedataextractor import GameDataExtractor

from keypath_extractor import Keypath


class EligibilityDataExtractor(GameDataExtractor):

    type = 'eligibility'

    @staticmethod
    def get_value_keypaths():
        return [
            Keypath('data.gender', 'Gender'),
            Keypath('data.gender-other', 'Gender Other'),
            Keypath('data.dob', 'DOB'),

            Keypath('data.height.unit1_val', 'Height Unit 1 Value'),
            Keypath('data.height.unit2_val', 'Height Unit 2 Value'),
            Keypath('data.height.units', 'Height Units'),

            Keypath('data.weight.unit1_val', 'Weight Unit 1 Value'),
            Keypath('data.weight.unit2_val', 'Weight Unit 2 Value'),
            Keypath('data.weight.units', 'Weight Units'),

            Keypath('data.allergies', 'Allergies'),
            Keypath('data.allergies-other', 'Allergies Other'),
            Keypath('data.eating-disorder', 'Allergies'),
            Keypath('data.eating-disorder-other', 'Allergies Other'),

            Keypath('data.bmi', 'BMI'),
            Keypath('data.age', 'Age'),
            Keypath('data.eligible', 'Eligible'),
            Keypath('data.height_cm', 'Height CM'),
            Keypath('data.weight_kgs', 'Weight KGs'),
        ]
