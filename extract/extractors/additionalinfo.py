from .dataextractor import DataExtractor


class AdditionalInfoDataExtractor(DataExtractor):

    type = 'additional-info'

    fields = [
        ('First Language', 'data.first-language'),
        ('First Language Other', 'data.first-language-other'),

        ('Ethnicity', 'data.ethnicity'),
        ('Ethnicity Other', 'data.ethnicity-other'),

        ('Country', 'data.country'),

        ('Hip Unit 1 Value', 'data.hip.unit1_val'),
        ('Hip Unit 2 Value', 'data.hip.unit2_val'),
        ('Hip Units', 'data.hip.units'),

        ('Waist Unit 1 Value', 'data.waist.unit1_val'),
        ('Waist Unit 2 Value', 'data.waist.unit2_val'),
        ('Waist Units', 'data.waist.units'),

        ('Health', 'data.health'),
        ('Health Other', 'data.health-other'),

        ('Weight Loss', 'data.weight-loss'),
        ('Weight Loss Other', 'data.weight-loss-other'),
        ('Weight Loss Success', 'data.weight-loss-success'),

        ('Additional Details', 'data.additional-details'),

        ('Smoking Status', 'data.smoking-status'),
        ('Smoking Status Other', 'data.smoking-status-other'),

        ('Weight Loss Success Other', 'data.weight-loss-success-other'),
        ('Waist CM', 'data.waist_cm'),
        ('Hip CM', 'data.hip_cm'),
    ]
