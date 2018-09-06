from .dataextractor import DataExtractor


class MeasuresDataExtractor(DataExtractor):

    type = 'measures'

    fields = [
        ('Emoji', 'data.emoji'),
        ('Fuel Gauge', 'data.fuel-gauge'),
        ('Last Eaten', 'data.last-eaten'),
    ]
