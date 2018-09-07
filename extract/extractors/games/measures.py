from .gamedataextractor import GameDataExtractor


class MeasuresDataExtractor(GameDataExtractor):

    type = 'measures'

    fields = [
        ('Emoji', 'data.emoji'),
        ('Fuel Gauge', 'data.fuel-gauge'),
        ('Last Eaten', 'data.last-eaten'),
    ]
