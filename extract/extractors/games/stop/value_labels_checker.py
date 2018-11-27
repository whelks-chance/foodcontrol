from pprint import pprint
from collections import defaultdict


class ValueLabelChecker:

    def __init__(self):
        self.label_allocation_counts = None
        self.label_allocation_item_id_percentages = None
        self.label_allocation_item_type_percentages = None
        self.selected_item_ids = None
        self.block_item_ids = None
        self.session_item_ids = None

    def check_value_labels(self, row):
        session_events = self.get_session_events(row)

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
            self.label_allocation_counts['HEALTHY']['1_'] / self.denominator(healthy_sum)
        self.label_allocation_item_id_percentages['HEALTHY']['2_'] =\
            self.label_allocation_counts['HEALTHY']['2_'] / self.denominator(healthy_sum)
        self.label_allocation_item_id_percentages['NON_HEALTHY']['1_'] =\
            self.label_allocation_counts['NON_HEALTHY']['1_'] / self.denominator(non_healthy_sum)
        self.label_allocation_item_id_percentages['NON_HEALTHY']['2_'] =\
            self.label_allocation_counts['NON_HEALTHY']['2_'] / self.denominator(non_healthy_sum)
        total_sum = healthy_sum + non_healthy_sum
        self.label_allocation_item_type_percentages = defaultdict(float)
        self.label_allocation_item_type_percentages['HEALTHY'] = healthy_sum / self.denominator(total_sum)
        self.label_allocation_item_type_percentages['NON_HEALTHY'] = non_healthy_sum / self.denominator(total_sum)

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
