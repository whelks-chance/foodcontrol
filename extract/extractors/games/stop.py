import statistics
from collections import defaultdict
from pprint import pprint

from .gamedataextractor import GameDataExtractor
from keypath_extractor import Keypath


class AbstractStopDataExtractor(GameDataExtractor):
    """The abstract base class for all STOP games"""

    @staticmethod
    def get_value_keypaths():
        return [
            Keypath('data.captureDate', 'Capture Date'),
        ]

    logs = []
    session_duration = 0
    durations = defaultdict(list)
    raw_count = {
        'on': defaultdict(int),
        'off': defaultdict(int)
    }

    def log_message(self, message, data=None):
        log = {
            'message': message,
            'data': data
        }
        pprint(log)
        self.logs.append(log)

    def log_message_if_check_failed(self, check_passed, trial, response, session_event):
        if not check_passed:
            message = 'Check failed: {} {} gameSessionID={} roundID={}, trialID={}'.format(
                                trial, response,
                                session_event['gameSessionID'], session_event['roundID'], session_event['trialID'])
            self.log_message(message, session_event)

    def clear(self):
        self.session_duration = 0
        self.durations.clear()
        self.session_trial_type_counts.clear()
        self.trial_type_block_count.clear()
        self.block_item_type_counts.clear()
        self.raw_count['on'].clear()
        self.raw_count['off'].clear()

    def check(self, row):
        super(AbstractStopDataExtractor, self).check(row)

        def check_trials_count():
            number_of_rounds = 4
            old_number_of_trials = 48
            new_number_of_trials = 24
            session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
            assert len(session_events) == (number_of_rounds * old_number_of_trials) or (number_of_rounds * new_number_of_trials)

        def check_trial_numbers():
            pass

        def check_value_labels():
            pass

        def check_points():
            pass

        check_trials_count()
        check_trial_numbers()
        check_value_labels()
        check_points()  # Called 'General checks' in the DataAnalysisBeta Word document

    @staticmethod
    def within_stimulus_boundaries(session_event, item_radius=95, prefix='tapResponsePosition'):
        tx = float(session_event['{}X'.format(prefix)])
        ty = float(session_event['{}Y'.format(prefix)])
        ix = session_event['itemPositionX']
        iy = session_event['itemPositionY']
        print(tx, ty, ix, iy)
        if ((tx - ix) ** 2) + ((ty - iy) ** 2) < (item_radius ** 2):
            return True
        else:
            return False

    def check(self, row):
        self.check_tap_responses(row)

    def numericify(self, n):
        if n is None:
            n = 0
        return n

    def check_tap_responses(self, row):
        print('check_tap_responses:', row['data'])
        session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
        for session_event in session_events:
            trial_type = session_event['trialType']
            tap_response_type = session_event['tapResponseType']
            if trial_type == 'GO':
                print('check_tap_responses: GO')
                tap_response_start = self.numericify(session_event['tapResponseStart'])
                if tap_response_type == 'CORRECT_GO':
                    check_passed = tap_response_start > 0 and self.within_stimulus_boundaries(session_event)
                    self.log_message_if_check_failed(check_passed, 'GO', 'CORRECT_GO', session_event)
                if tap_response_type == 'INCORRECT_GO':
                    check_passed = tap_response_start == 0
                    self.log_message_if_check_failed(check_passed, 'GO', 'INCORRECT_GO', session_event)
                if tap_response_type == 'MISS_GO':
                    check_passed = tap_response_start > 0 and not self.within_stimulus_boundaries(session_event)
                    self.log_message_if_check_failed(check_passed, 'GO', 'MISS_GO', session_event)

            if trial_type == 'STOP':
                print('check_tap_responses: STOP')
                if tap_response_type == 'CORRECT_GO':
                    check_passed = session_event['tapResponseStart'] == 0
                    self.log_message_if_check_failed(check_passed, 'STOP', 'CORRECT_GO', session_event)
                if tap_response_type == 'INCORRECT_GO':
                    check_passed = session_event['tapResponseStart'] > 0 and self.within_stimulus_boundaries(session_event)
                    self.log_message_if_check_failed(check_passed, 'STOP', 'INCORRECT_GO', session_event)
                if tap_response_type == 'MISS_STOP':
                    check_passed = session_event['tapResponseStart'] > 0 and not self.within_stimulus_boundaries(session_event)
                    self.log_message_if_check_failed(check_passed, 'STOP', 'MISS_STOP', session_event)

    def calculate(self, row):
        super(AbstractStopDataExtractor, self).calculate(row)

        def calculate_durations():
            # "Durations"

            def calculate_session_duration():
                session_start = self.get_keypath_value(row, 'data.0.sessionStart')
                session_end = self.get_keypath_value(row, 'data.0.sessionEnd')
                self.session_duration = session_start - session_end

            def record_duration(key, value):
                self.durations[key].append(value)

            def get_session_events(row):
                """
                Handle inconsistently formatted data structures:
                data -> object vs data -> [ object ]
                """
                session_events = None
                try:
                    session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
                except KeyError:
                    try:
                        session_events = self.get_keypath_value(row, 'data.sessionEvents')
                    except KeyError:
                        pass
                return session_events

            def calculate_trial_durations():

                def not_none(a, b):
                    return a is not None and b is not None

                session_events = get_session_events(row)
                if session_events:
                    previous_session_event = None
                    for session_event in session_events:
                        trial_start = session_event['trialStart']
                        trial_end = session_event['trialEnd']
                        trial_duration = trial_end - trial_start
                        record_duration('trial', trial_duration)

                        stop_signal_onset = session_event['stopSignalOnset']
                        stop_signal_offset = session_event['stopSignalOffset']
                        if not_none(stop_signal_onset, stop_signal_offset):
                            stop_signal_duration = stop_signal_offset - stop_signal_onset
                            record_duration('stop_signal', stop_signal_duration)

                        stimulus_onset = session_event['stimulusOnset']
                        stimulus_offset = session_event['stimulusOffset']
                        if not_none(stimulus_onset, stimulus_offset):
                            stimulus_duration = stimulus_offset - stimulus_onset
                            record_duration('stimulus', stimulus_duration)

                        # Difference between signal onset and stop signal delay
                        stop_signal_delay = session_event['stopSignalDelay']
                        if not_none(stop_signal_onset, stop_signal_delay):
                            signal_stop_difference = stop_signal_onset - stop_signal_delay
                            record_duration('signal_stop_difference', signal_stop_difference)

                        # Duration between signal offset and stimulus offset
                        if not_none(stimulus_offset, stop_signal_offset):
                            stimulus_stop_difference = stimulus_offset - stop_signal_offset
                            record_duration('stimulus_stop_difference', stimulus_stop_difference)

                        if previous_session_event:
                            previous_trial_start = previous_session_event['trialStart']
                            inter_trial_duration = trial_start - previous_trial_start
                            record_duration('inter_trial', inter_trial_duration)

                        previous_session_event = session_event

            def calculate_trial_duration_stats():

                def remove_none_values(values):
                    return [d for d in values if d is not None]

                def calculate_stats(durations_key):
                    durations = remove_none_values(self.durations[durations_key])
                    return {
                        'min': min(durations),
                        'max': max(durations),
                        'mean': statistics.mean(durations),
                        'stdev': statistics.stdev(durations),
                    }

                trial_categories = [
                    'trial',
                    'stop_signal',
                    'stimulus',
                    'signal_stop_difference',
                    'stimulus_stop_difference',
                    'inter_trial'
                ]

                self.trial_stats = {}
                for trial_category in trial_categories:
                    self.trial_stats[trial_category] = calculate_stats(trial_category)

            calculate_session_duration()
            calculate_trial_durations()
            calculate_trial_duration_stats()

        def count_trial_and_types():
            self.trial_count = 0
            self.raw_round_trial_counts = defaultdict(set)
            self.block_trial_type_counts = defaultdict(lambda: defaultdict(int))  # dict of int dict
            self.block_item_type_counts = defaultdict(lambda: defaultdict(int))   # dict of int dict

            session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
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
                    self.block_trial_type_percentages[block_id_key][item_key] = self.block_trial_type_counts[block_id_key][item_key] / block_total

            # Calculate the block-level item type percentages
            self.block_item_type_percentages = defaultdict(lambda: defaultdict(float))  # dict of float dict
            for block_id_key, items in self.block_item_type_counts.items():
                block_total = 0
                for item_key, item_count in items.items():
                    block_total += item_count
                for item_key, item_count in items.items():
                    self.block_item_type_percentages[block_id_key][item_key] = self.block_item_type_counts[block_id_key][item_key] / block_total

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

        def count_raw_events():
            # "Raw data"
            raw_events = self.get_keypath_value(row, 'data.0.rawEvents')
            for raw_event in raw_events:
                self.raw_count['on'][raw_event['eventOn']] += 1
                self.raw_count['off'][raw_event['eventOff']] += 1

        def check_value_labels():
            session_events = self.get_keypath_value(row, 'data.0.sessionEvents')

            # Record healthy/non-healthy label allocation counts
            self.label_allocation_counts = defaultdict(lambda: defaultdict(int))  # dict of int dict
            for session_event in session_events:
                item_id = session_event['itemID']
                item_type = session_event['itemType']
                for prefix in ['1_', '2_']:
                    if item_id.startswith(prefix):
                        self.label_allocation_counts[item_type][prefix] += 1

            # Record healthy/non-healthy label allocation percentages
            # TODO

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

        calculate_durations()
        count_trial_and_types()
        count_raw_events()
        check_value_labels()

        print('TRIAL COUNT: ', self.trial_count)

        print('\nRAW COUNTS:')
        print(' ON', self.raw_count['on'])
        print('OFF', self.raw_count['off'])

        print('\nTRIAL DURATIONS:')
        for key in self.durations:
            print(key, self.durations[key])

        print('\nTRIAL STATS:')
        pprint(self.trial_stats)

        # Trial Types
        print('\nSESSION TRIAL TYPE COUNTS:')
        pprint(self.session_trial_type_counts)
        print('\nSESSION TRIAL TYPE PERCENTAGES:')
        pprint(self.session_trial_type_percentages)
        print('\nBLOCK TRIAL TYPE COUNTS:')
        pprint(self.block_trial_type_counts)
        print('\nBLOCK TRIAL TYPE PERCENTAGES:')
        pprint(self.block_trial_type_percentages)

        # Trial Items
        print('\nSESSION ITEM TYPE COUNTS:')
        pprint(self.session_item_type_counts)
        print('\nSESSION ITEM TYPE PERCENTAGES:')
        pprint(self.session_item_type_percentages)
        print('\nBLOCK ITEM TYPE COUNTS:')
        pprint(self.block_item_type_counts)
        print('\nBLOCK ITEM TYPE PERCENTAGES:')
        pprint(self.block_item_type_percentages)

        print('\nRAW ROUND TRIAL COUNTS:')
        for key in self.raw_round_trial_counts:
            print(key, len(self.raw_round_trial_counts[key]), self.raw_round_trial_counts[key])

        # Label Allocation Counts
        print('\nLABEL ALLOCATION COUNTS:')
        pprint(self.label_allocation_counts)

        # Selected Item IDs
        print('\nSELCTED ITEM IDs:')
        pprint(self.selected_item_ids)

        # Unique Item IDs
        print('\nSESSION ITEM IDs:')
        pprint(self.session_item_ids)
        print('\nBLOCK ITEM IDs:')
        pprint(self.block_item_ids)

        print('\nLog')
        for log in self.logs:
            print(log['message'])


class StopDataExtractor(AbstractStopDataExtractor):

    type = 'STOP'


class RestraintDataExtractor(AbstractStopDataExtractor):

    type = 'RESTRAINT'


class NAStopDataExtractor(AbstractStopDataExtractor):

    type = 'NASTOP'


class NARestraintDataExtractor(AbstractStopDataExtractor):

    type = 'NARESTRAINT'


class GStopDataExtractor(AbstractStopDataExtractor):

    type = 'GSTOP'


class GRestraintDataExtractor(AbstractStopDataExtractor):

    type = 'GRESTRAINT'


class DoubleDataExtractor(AbstractStopDataExtractor):

    type = 'DOUBLE'

    def check_tap_responses(self, row):
        print('check_tap_responses:', row['data'])
        # assert False

    def check(self, row):
        super(DoubleDataExtractor, self).check(row)

        def check_initial_response_type():
            pass

        def check_second_response_type():
            pass

        def check_points():
            pass

        check_initial_response_type()
        check_second_response_type()
        check_points()

    def calculate(self, row):
        super(DoubleDataExtractor, self).calculate(row)
