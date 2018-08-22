from collections import defaultdict

from .dataextractor import DataExtractor


class VirtualSupermarketDataExtractor(DataExtractor):

    type = 'virtual-supermarket-selected'

    fields = []

    vs_column_names = [
        'Shop Number',
        'Shop Name',
        'Shop Type',
        'Item ID',
        'Item Name',
        'Item Selected',
    ]

    selected_value_count = defaultdict(int)

    vs_values = {}

    def clear(self):
        super(VirtualSupermarketDataExtractor, self).clear()
        self.selected_value_count.clear()

    def column_names(self):
        """Override to provide bespoke column names for this game"""
        common_field_names = [column_name for column_name, _ in self.common_fields]
        return common_field_names + self.vs_column_names

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
