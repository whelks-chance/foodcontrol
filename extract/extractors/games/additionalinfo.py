from .gamedataextractor import GameDataExtractor

from keypath_extractor import Keypath


class AdditionalInfoDataExtractor(GameDataExtractor):

    type = 'additional-info'

    def get_value_keypaths(self):
        return [
            Keypath('data.first-language', 'First Language'),
            Keypath('data.first-language-other', 'First Language Other'),

            Keypath('data.ethnicity', 'Ethnicity'),
            Keypath('data.ethnicity-other', 'Ethnicity Other'),

            Keypath('data.country', 'Country'),

            Keypath('data.hip.unit1_val', 'Hip Unit 1 Value'),
            Keypath('data.hip.unit2_val', 'Hip Unit 2 Value'),
            Keypath('data.hip.units', 'Hip Units'),

            Keypath('data.waist.unit1_val', 'Waist Unit 1 Value'),
            Keypath('data.waist.unit2_val', 'Waist Unit 2 Value'),
            Keypath('data.waist.units', 'Waist Units'),

            Keypath('data.health', 'Health'),
            Keypath('data.health-other', 'Health Other'),

            Keypath('data.weight-loss', 'Weight Loss'),
            Keypath('data.weight-loss-other', 'Weight Loss Other'),
            Keypath('data.weight-loss-success', 'Weight Loss Success'),

            Keypath('data.additional-details', 'Additional Details'),

            Keypath('data.smoking-status', 'Smoking Status'),
            Keypath('data.smoking-status-other', 'Smoking Status Other'),

            Keypath('data.weight-loss-success-other', 'Weight Loss Success Other'),
            Keypath('data.waist_cm', 'Waist CM'),
            Keypath('data.hip_cm', 'Hip CM'),
        ]
