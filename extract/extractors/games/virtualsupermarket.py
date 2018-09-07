from collections import defaultdict

from ..dataextractor import DataExtractor


class VirtualSupermarketDataExtractor(DataExtractor):

    type = 'virtual-supermarket-selected'

    fields = []

    derived_fields = [
        (None, 'Shop Number', 'shop_number'),
        (None, 'Shop Name', 'shop_name'),
        (None, 'Shop Type', 'shop_type'),
        (None, 'Item ID', 'item_id'),
        (None, 'Item Name', 'item_name'),
        (None, 'Item Selected', 'item_selected'),
    ]

    selected_value_count = defaultdict(int)

    vs_values = {}

    def clear(self):
        super().clear()
        self.selected_value_count.clear()

    def extract(self, row):
        """Override to provide bespoke field extraction for this game"""
        self.clear()
        # print('VirtualSupermarketDataExtractor.extract()')
        # TODO: Implement for this game

    def calculate(self, row):

        def update_selected_values_count():

            def update_selected_values_count_for_keypath(keypath):
                items = row.get_keypath_value(keypath)
                for item in items:
                    selected_value = item['selected']
                    self.selected_value_count[selected_value] += 1

            update_selected_values_count_for_keypath('data.shop1.items')
            update_selected_values_count_for_keypath('data.shop2.items')

        update_selected_values_count()
