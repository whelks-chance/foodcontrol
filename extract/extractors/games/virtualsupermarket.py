from collections import defaultdict

from .gamedataextractor import GameDataExtractor

from keypath_extractor import Keypath


class VirtualSupermarketDataExtractor(GameDataExtractor):

    type = 'virtual-supermarket-selected'

    common_shop_keypaths = [
        Keypath('shop', 'Shop'),
        Keypath('type', 'Type'),
        Keypath('name', 'Name')
    ]

    item_keypaths = [
        Keypath('id', 'Item ID'),
        Keypath('name', 'Item Name'),
        Keypath('selected', 'Item Selected')
    ]

    def get_value_keypaths_for_naming_columns(self):
        return self.common_shop_keypaths + self.item_keypaths

    def extract_shop_rows(self, common_values, common_shop_values, shop_data):
        rows = []
        for item in shop_data['items']:
            shop_values = self.extract_values_with_keypaths(self.item_keypaths, [], item)
            shop_values.update(common_shop_values)
            shop_values.update(common_values)
            rows.append(shop_values)
        return rows

    def extract_values(self, data):
        common_values = self.extract_values_with_keypaths(self.get_common_keypaths(), [], data)
        rows = []
        for shop_number in ['shop1', 'shop2']:
            shop_data = data['data'][shop_number]
            shop_data['shop'] = shop_number  # add this key-encoded data as a value to extract it with a keypath
            common_shop_values = self.extract_values_with_keypaths(self.common_shop_keypaths, [], shop_data)
            shop_rows = self.extract_shop_rows(common_values, common_shop_values, shop_data)
            rows += shop_rows
        return rows

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
