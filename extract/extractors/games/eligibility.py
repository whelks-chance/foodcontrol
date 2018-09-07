from ..dataextractor import DataExtractor


class EligibilityDataExtractor(DataExtractor):

    type = 'eligibility'

    fields = [
        ('Gender', 'data.gender'),
        ('Gender Other', 'data.gender-other'),
        ('DOB', 'data.dob'),

        ('Height Unit 1 Value', 'data.height.unit1_val'),
        ('Height Unit 2 Value', 'data.height.unit2_val'),
        ('Height Units', 'data.height.units'),

        ('Weight Unit 1 Value', 'data.weight.unit1_val'),
        ('Weight Unit 2 Value', 'data.weight.unit2_val'),
        ('Weight Units', 'data.weight.units'),

        ('Allergies', 'data.allergies'),
        ('Allergies Other', 'data.allergies-other'),

        ('Allergies', 'data.eating-disorder'),
        ('Allergies Other', 'data.eating-disorder-other'),

        ('BMI', 'data.bmi'),
        ('Age', 'data.age'),
        ('Eligible', 'data.eligible'),
        ('Height CM', 'data.height_cm'),
        ('Weight KGs', 'data.weight_kgs'),
    ]
