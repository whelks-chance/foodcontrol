from collections import defaultdict

from .gamedataextractor import GameDataExtractor


class VirtualSupermarketDataExtractor(GameDataExtractor):

    type = 'virtual-supermarket-selected'

    # derived_fields = [
    #     (None, 'Shop Number', 'shop_number'),
    #     (None, 'Shop Name', 'shop_name'),
    #     (None, 'Shop Type', 'shop_type'),
    #     (None, 'Item ID', 'item_id'),
    #     (None, 'Item Name', 'item_name'),
    #     (None, 'Item Selected', 'item_selected'),
    # ]

    selected_value_count = defaultdict(int)

    def calculate(self, row):

        def update_selected_values_count():

            def update_selected_values_count_for_keypath(keypath):
                items = self.get_keypath_value(row, keypath)
                for item in items:
                    selected_value = item['selected']
                    self.selected_value_count[selected_value] += 1

            update_selected_values_count_for_keypath('data.shop1.items')
            update_selected_values_count_for_keypath('data.shop2.items')

        update_selected_values_count()
