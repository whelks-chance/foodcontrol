from collections import defaultdict

from .dataextractor import DataExtractor


class VirtualSupermarketDataExtractor(DataExtractor):

    type = 'virtual-supermarket-selected'

    fields = [
    ]

    selected_value_count = defaultdict(int)

    def clear(self):
        super(VirtualSupermarketDataExtractor, self).clear()
        self.selected_value_count.clear()

    def calculate(self, row):

        def update_selected_values_count():

            def update_selected_values_count_for_keypath(keypath):
                items = self.value(row, keypath)
                for item in items:
                    selected_value = item['selected']
                    self.selected_value_count[selected_value] += 1

            update_selected_values_count_for_keypath('data.shop1.items')
            update_selected_values_count_for_keypath('data.shop2.items')

        update_selected_values_count()
