from .gamedataextractor import GameDataExtractor


class EligibilityDataExtractor(GameDataExtractor):

    type = 'eligibility'

    @staticmethod
    def get_value_keypaths():
        return [
            ('data.gender', 'Gender'),
            ('data.gender-other', 'Gender Other'),
            ('data.dob', 'DOB'),

            ('data.height.unit1_val', 'Height Unit 1 Value'),
            ('data.height.unit2_val', 'Height Unit 2 Value'),
            ('data.height.units', 'Height Units'),

            ('data.weight.unit1_val', 'Weight Unit 1 Value'),
            ('data.weight.unit2_val', 'Weight Unit 2 Value'),
            ('data.weight.units', 'Weight Units'),

            ('data.allergies', 'Allergies'),
            ('data.allergies-other', 'Allergies Other'),
            ('data.eating-disorder', 'Allergies'),
            ('data.eating-disorder-other', 'Allergies Other'),

            ('data.bmi', 'BMI'),
            ('data.age', 'Age'),
            ('data.eligible', 'Eligible'),
            ('data.height_cm', 'Height CM'),
            ('data.weight_kgs', 'Weight KGs'),
        ]
