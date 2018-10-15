from .gamedataextractor import GameDataExtractor

from keypath_extractor import Keypath


class MeasuresDataExtractor(GameDataExtractor):

    type = 'measures'

    @staticmethod
    def get_value_keypaths():
        return [
            Keypath('data.emoji', 'Emoji'),
            Keypath('data.fuel-gauge', 'Fuel Gauge'),
            Keypath('data.last-eaten', 'Last Eaten'),
        ]
