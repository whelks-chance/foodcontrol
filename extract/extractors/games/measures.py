from .gamedataextractor import GameDataExtractor


class MeasuresDataExtractor(GameDataExtractor):

    type = 'measures'

    @staticmethod
    def get_value_keypaths():
        return [
            ('data.emoji', 'Emoji'),
            ('data.fuel-gauge', 'Fuel Gauge'),
            ('data.last-eaten', 'Last Eaten'),
        ]
