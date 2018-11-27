from pprint import pprint
from collections import defaultdict

from .abstract_stop_evaluator import AbstractStopEvaluator

from utils import irange, get_session_events


class TrialTypesCalculator(AbstractStopEvaluator):

    def __init__(self):
        self.trial_count = None
        self.raw_round_trial_counts = None
        self.block_trial_type_counts = None
        self.block_item_type_counts = None
        self.block_trial_type_percentages = None
        self.block_item_type_percentages = None
        self.session_trial_type_counts = None
        self.session_trial_type_percentages = None
        self.session_item_type_counts = None
        self.session_item_type_percentages = None

    def evaluate(self, row):
        self.count_trial_and_types(row)

    def count_trial_and_types(self, row):
        session_events = get_session_events(row)

        self.trial_count = 0
        self.raw_round_trial_counts = defaultdict(set)
        self.block_trial_type_counts = defaultdict(lambda: defaultdict(int))  # dict of int dict
        self.block_item_type_counts = defaultdict(lambda: defaultdict(int))  # dict of int dict
        for session_event in session_events:
            self.trial_count += 1

            # Create a set of the trial IDs so we can count the elements
            block_id = session_event['roundID']
            trial_id = session_event['trialID']
            self.raw_round_trial_counts[block_id].add(trial_id)

            # Record the block-level trial type counts (GO/STOP)
            trial_type = session_event['trialType']
            self.block_trial_type_counts[block_id][trial_type] += 1

            # Record the block-level item type counts (HEALTHY/NON-HEALTHY)
            item_type = session_event['itemType']
            selected = session_event['selected']
            if item_type == 'HEALTHY':
                self.block_item_type_counts[block_id]['HEALTHY'] += 1
                if selected == 'random':
                    self.block_item_type_counts[block_id]['HEALTHY_RANDOM'] += 1
                else:
                    self.block_item_type_counts[block_id]['HEALTHY_NOT_RANDOM'] += 1
            if item_type == 'NON_HEALTHY':
                self.block_item_type_counts[block_id]['NON_HEALTHY'] += 1

        # Calculate the block-level trial type percentages
        self.block_trial_type_percentages = defaultdict(lambda: defaultdict(float))  # dict of float dict
        for block_id_key, items in self.block_trial_type_counts.items():
            block_total = 0
            for item_key, item_count in items.items():
                block_total += item_count
            for item_key, item_count in items.items():
                self.block_trial_type_percentages[block_id_key][item_key] =\
                    self.block_trial_type_counts[block_id_key][item_key] / block_total

        # Calculate the block-level item type percentages
        self.block_item_type_percentages = defaultdict(lambda: defaultdict(float))  # dict of float dict
        for block_id_key, items in self.block_item_type_counts.items():
            block_total = 0
            for item_key, item_count in items.items():
                block_total += item_count
            for item_key, item_count in items.items():
                self.block_item_type_percentages[block_id_key][item_key] =\
                    self.block_item_type_counts[block_id_key][item_key] / block_total

        # Calculate the session-level trial type counts from the block-level counts
        self.session_trial_type_counts = defaultdict(int)
        for block_id_key, items in self.block_trial_type_counts.items():
            for item_key, item_count in items.items():
                self.session_trial_type_counts[item_key] += item_count

        # Calculate the session-level trial type percentages
        self.session_trial_type_percentages = defaultdict(float)
        for trial_type, trial_type_count in self.session_trial_type_counts.items():
            self.session_trial_type_percentages[trial_type] = trial_type_count / self.trial_count

        # Calculate the session-level item type counts from the block-level counts
        self.session_item_type_counts = defaultdict(int)
        for block_id_key, items in self.block_item_type_counts.items():
            for item_key, item_count in items.items():
                self.session_item_type_counts[item_key] += item_count

        # Calculate the session-level item type percentages
        self.session_item_type_percentages = defaultdict(float)
        for item_type, item_type_count in self.session_item_type_counts.items():
            self.session_item_type_percentages[item_type] = item_type_count / self.trial_count
