from pprint import pprint
from collections import defaultdict

from .abstract_stop_evaluator import AbstractStopEvaluator

from utils import irange, get_session_events, denominator


class ValueLabelChecker(AbstractStopEvaluator):

    def __init__(self):
        self.label_allocation_counts = None
        self.label_allocation_item_id_percentages = None
        self.label_allocation_item_type_percentages = None
        self.selected_item_ids = None
        self.block_item_ids = None
        self.session_item_ids = None

    def evaluate(self, row):
        self.check_value_labels(row)
        self.record_item_ids(row)

    def check_value_labels(self, row):
        session_events = get_session_events(row)

        # Record healthy/non-healthy label allocation counts
        self.label_allocation_counts = defaultdict(lambda: defaultdict(int))  # dict of int dict
        self.label_allocation_counts['HEALTHY']['1_'] = 0
        self.label_allocation_counts['HEALTHY']['2_'] = 0
        self.label_allocation_counts['NON_HEALTHY']['1_'] = 0
        self.label_allocation_counts['NON_HEALTHY']['2_'] = 0
        for session_event in session_events:
            item_id = session_event['itemID']
            item_type = session_event['itemType']
            for prefix in ['1_', '2_']:
                if item_id.startswith(prefix):
                    self.label_allocation_counts[item_type][prefix] += 1

        # Record healthy/non-healthy label allocation percentages
        self.label_allocation_item_id_percentages = defaultdict(lambda: defaultdict(float))  # dict of int dict
        healthy_sum = self.label_allocation_counts['HEALTHY']['1_'] + self.label_allocation_counts['HEALTHY']['2_']
        pprint(self.label_allocation_counts)
        non_healthy_sum = self.label_allocation_counts['NON_HEALTHY']['1_'] + \
            self.label_allocation_counts['NON_HEALTHY']['2_']
        self.label_allocation_item_id_percentages['HEALTHY']['1_'] =\
            self.label_allocation_counts['HEALTHY']['1_'] / denominator(healthy_sum)
        self.label_allocation_item_id_percentages['HEALTHY']['2_'] =\
            self.label_allocation_counts['HEALTHY']['2_'] / denominator(healthy_sum)
        self.label_allocation_item_id_percentages['NON_HEALTHY']['1_'] =\
            self.label_allocation_counts['NON_HEALTHY']['1_'] / denominator(non_healthy_sum)
        self.label_allocation_item_id_percentages['NON_HEALTHY']['2_'] =\
            self.label_allocation_counts['NON_HEALTHY']['2_'] / denominator(non_healthy_sum)
        total_sum = healthy_sum + non_healthy_sum
        self.label_allocation_item_type_percentages = defaultdict(float)
        self.label_allocation_item_type_percentages['HEALTHY'] = healthy_sum / denominator(total_sum)
        self.label_allocation_item_type_percentages['NON_HEALTHY'] = non_healthy_sum / denominator(total_sum)

    def record_item_ids(self, row):
        session_events = get_session_events(row)

        # Record the item IDs for each value of selected (MB/random/user/upload/non-food)
        self.selected_item_ids = defaultdict(set)  # dict of set
        for session_event in session_events:
            selected = session_event['selected']
            item_id = session_event['itemID']
            self.selected_item_ids[selected].add(item_id)

        # Record the block-level set of unique item IDs
        self.block_item_ids = defaultdict(set)  # dict of set
        for session_event in session_events:
            block_id = session_event['roundID']
            item_id = session_event['itemID']
            self.block_item_ids[block_id].add(item_id)

        # Record the session-level set of unique item IDs
        self.session_item_ids = set()
        for _, item_ids in self.block_item_ids.items():
            self.session_item_ids.update(item_ids)

    def populate_spreadsheet(self, spreadsheet):
        self.populate_label_allocations(spreadsheet)
        self.populate_item_ids(spreadsheet)

    def populate_label_allocations(self, spreadsheet):
        spreadsheet.select_sheet('Label Allocations')

        # - Counts
        spreadsheet.set_values(['Session'])
        spreadsheet.set_values(['Trial Type', 'Prefix', 'Count', 'Percentage'])
        for item_type in ['HEALTHY', 'NON_HEALTHY']:
            for prefix in ['1_', '2_']:
                spreadsheet.set_values([
                    item_type,
                    prefix,
                    self.label_allocation_counts[item_type][prefix],
                    self.label_allocation_item_id_percentages[item_type][prefix]
                ])
        print('\nLABEL ALLOCATION COUNTS:')
        pprint(self.label_allocation_counts)

        # - Percentages
        spreadsheet.advance_row()
        spreadsheet.set_values(['Item Type', 'Percentage'])
        for item_type in self.label_allocation_item_type_percentages:
            spreadsheet.set_values([
                item_type,
                self.label_allocation_item_type_percentages[item_type]
            ])
        print('\nLABEL ALLOCATION PERCENTAGES:')
        pprint(self.label_allocation_item_id_percentages)
        pprint(self.label_allocation_item_type_percentages)

    def populate_item_ids(self, spreadsheet):
        # Selected Item IDs
        spreadsheet.select_sheet('Selected Items')
        for index, selected_label in enumerate(self.selected_item_ids):
            spreadsheet.set_values([selected_label])
        for index, selected_label in enumerate(self.selected_item_ids):
            for i, selected_item_id in enumerate(self.selected_item_ids[selected_label]):
                spreadsheet.set_values([selected_item_id])
        print('\nSELCTED ITEM IDs:')
        print(self.selected_item_ids)

        # Unique Item IDs
        # - Session
        spreadsheet.select_sheet('Unique Items - Session')
        for index, unique_item_id in enumerate(self.session_item_ids):
            spreadsheet.set_values([unique_item_id])
        # - Blocks
        spreadsheet.select_sheet('Unique Items - Blocks')
        for block_key in irange(1, 4):
            spreadsheet.set_value(block_key)
        spreadsheet.advance_row()
        for block_key in irange(1, 4):
            for index, unique_item_id in enumerate(self.block_item_ids[block_key]):
                spreadsheet.column = block_key
                spreadsheet.set_value(unique_item_id, cell_offset=(block_key, index+1))

        print('\nSESSION ITEM IDs:')
        print(self.session_item_ids)
        print('\nBLOCK ITEM IDs:')
        pprint(self.block_item_ids)
