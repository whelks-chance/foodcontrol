from .gamedataextractor import GameDataExtractor


class AdditionalInfoDataExtractor(GameDataExtractor):

    type = 'additional-info'

    @staticmethod
    def get_value_keypaths():
        return [
            ('data.first-language', 'First Language'),
            ('data.first-language-other', 'First Language Other'),

            ('data.ethnicity', 'Ethnicity'),
            ('data.ethnicity-other', 'Ethnicity Other'),

            ('data.country', 'Country'),

            ('data.hip.unit1_val', 'Hip Unit 1 Value'),
            ('data.hip.unit2_val', 'Hip Unit 2 Value'),
            ('data.hip.units', 'Hip Units'),

            ('data.waist.unit1_val', 'Waist Unit 1 Value'),
            ('data.waist.unit2_val', 'Waist Unit 2 Value'),
            ('data.waist.units', 'Waist Units'),

            ('data.health', 'Health'),
            ('data.health-other', 'Health Other'),

            ('data.weight-loss', 'Weight Loss'),
            ('data.weight-loss-other', 'Weight Loss Other'),
            ('data.weight-loss-success', 'Weight Loss Success'),

            ('data.additional-details', 'Additional Details'),

            ('data.smoking-status', 'Smoking Status'),
            ('data.smoking-status-other', 'Smoking Status Other'),

            ('data.weight-loss-success-other', 'Weight Loss Success Other'),
            ('data.waist_cm', 'Waist CM'),
            ('data.hip_cm', 'Hip CM'),
        ]
