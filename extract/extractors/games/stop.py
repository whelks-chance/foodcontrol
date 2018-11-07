import statistics
from collections import defaultdict
from openpyxl import Workbook
from pprint import pprint

from .gamedataextractor import GameDataExtractor
from .session_event_log import SessionEventLog
from keypath_extractor import Keypath
from utils import irange


class AbstractStopDataExtractor(GameDataExtractor):
    """The abstract base class for all STOP games"""

    @staticmethod
    def get_value_keypaths():
        return [
            Keypath('data.captureDate', 'Capture Date'),
        ]

    session_event_log = SessionEventLog()
    session_duration = 0
    durations = defaultdict(list)
    raw_count = {
        'on': defaultdict(int),
        'off': defaultdict(int)
    }

    @staticmethod
    def numericify(n):
        if n is None:
            n = 0
        return n

    @staticmethod
    def denominator(n):
        if n:
            return n
        else:
            return 1

    @staticmethod
    def mean(numbers):
        if numbers and len(numbers) > 0:
            return statistics.mean(numbers)
        else:
            return 0

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

        check_trials_count()

    def check(self, row):
        self.check_tap_responses(row)

    def get_session_events(self, row):
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

    @staticmethod
    def within_stimulus_boundaries(session_event, item_radius=95, prefix='tapResponsePosition'):
        tx = float(session_event['{}X'.format(prefix)])
        ty = float(session_event['{}Y'.format(prefix)])
        ix = session_event['itemPositionX']
        iy = session_event['itemPositionY']
        # print(tx, ty, ix, iy)
        if ((tx - ix) ** 2) + ((ty - iy) ** 2) < (item_radius ** 2):
            return True
        else:
            return False

    def check_tap_responses(self, row):
        session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
        for session_event in session_events:
            trial_type = session_event['trialType']
            tap_response_type = session_event['tapResponseType']
            tap_response_start = self.numericify(session_event['tapResponseStart'])
            if trial_type == 'GO':
                if tap_response_type == 'CORRECT_GO':
                    check_passed = tap_response_start > 0 and self.within_stimulus_boundaries(session_event)
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if tap_response_type == 'INCORRECT_GO':
                    check_passed = tap_response_start == 0
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if tap_response_type == 'MISS_GO':
                    check_passed = tap_response_start > 0 and not self.within_stimulus_boundaries(session_event)
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)

            if trial_type == 'STOP':
                if tap_response_type == 'CORRECT_GO':
                    check_passed = tap_response_start == 0
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if tap_response_type == 'INCORRECT_GO':
                    check_passed = tap_response_start > 0 and self.within_stimulus_boundaries(session_event)
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if tap_response_type == 'MISS_STOP':
                    check_passed = tap_response_start > 0 and not self.within_stimulus_boundaries(session_event)
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)

    def check_points(self, row):
        points = {
            'GO': {
                'CORRECT_GO': 20,
                'INCORRECT_GO': -50,
                'MISS_GO': -20,
            },
            'STOP': {
                'CORRECT_STOP': 50,
                'INCORRECT_STOP': -50,
                'MISS_STOP': -50,
            }
        }
        running_total = 0
        session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
        for session_event in session_events:
            trial_type = session_event['trialType']
            tap_response_type = session_event['tapResponseType']
            points_this_trial = session_event['pointsThisTrial']
            assert points_this_trial == points[trial_type][tap_response_type]
            running_total += points_this_trial
            points_running_total = session_event['pointsRunningTotal']
            assert points_running_total == running_total

    def calculate_ssrt(self, row):
        session_events = self.get_session_events(row)
        if session_events:

            # Mean SSRT
            tap_response_start_total = 0
            stop_signal_delay_total = 0
            stop_signal_onset_total = 0
            for session_event in session_events:
                trial_type = session_event['trialType']
                tap_response_start = self.numericify(session_event['tapResponseStart'])
                if trial_type == 'GO' and tap_response_start > 0:
                    tap_response_start_total += tap_response_start
                stop_signal_delay = self.numericify(session_event['stopSignalDelay'])
                stop_signal_delay_total += stop_signal_delay
                stop_signal_onset = self.numericify(session_event['stopSignalOnset'])
                stop_signal_onset_total += stop_signal_onset
            mean_tap_response_start = tap_response_start_total / len(session_events)
            mean_stop_signal_delay = stop_signal_delay_total / len(session_events)
            mean_stop_signal_onset = stop_signal_onset_total / len(session_events)
            mean_ideal_ssrt = mean_tap_response_start - mean_stop_signal_delay  # What the SSRT should be
            mean_actual_ssrt = mean_tap_response_start - mean_stop_signal_onset  # What the SSRT actually is
            print('\n IDEAL MEAN SSRT:', mean_ideal_ssrt)
            print('ACTUAL MEAN SSRT:', mean_actual_ssrt)

            # Integration SSRT
            incorrect_stop_trials_count = 0
            for session_event in session_events:
                tap_response_type = session_event['tapResponseType']
                if tap_response_type == 'INCORRECT_STOP' or tap_response_type == 'MISS_STOP':
                    incorrect_stop_trials_count += 1
            print('INCORRECT STOP TRIALS:', incorrect_stop_trials_count)

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

            def calculate_trial_durations():

                def not_none(a, b):
                    return a is not None and b is not None

                session_events = self.get_session_events(row)
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
            non_healthy_sum = self.label_allocation_counts['NON_HEALTHY']['1_'] + self.label_allocation_counts['NON_HEALTHY']['2_']
            self.label_allocation_item_id_percentages['HEALTHY']['1_'] = self.label_allocation_counts['HEALTHY']['1_'] / self.denominator(healthy_sum)
            self.label_allocation_item_id_percentages['HEALTHY']['2_'] = self.label_allocation_counts['HEALTHY']['2_'] / self.denominator(healthy_sum)
            self.label_allocation_item_id_percentages['NON_HEALTHY']['1_'] = self.label_allocation_counts['NON_HEALTHY']['1_'] / self.denominator(non_healthy_sum)
            self.label_allocation_item_id_percentages['NON_HEALTHY']['2_'] = self.label_allocation_counts['NON_HEALTHY']['2_'] / self.denominator(non_healthy_sum)
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

        def calculate_dependent_variables():
            self.dv_correct_counts = defaultdict(lambda: defaultdict(int))
            session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
            trial_count = len(session_events)
            for session_event in session_events:
                # GO/STOP
                if 'tapResponseType' in session_event:
                    tap_response_type = session_event['tapResponseType']
                    if tap_response_type == 'CORRECT_GO' or tap_response_type == 'CORRECT_STOP':
                        block_id = session_event['roundID']
                        self.dv_correct_counts[block_id][tap_response_type] += 1

            # Calculate the CORRECT_GO/STOP block-level percentages
            self.dv_correct_block_percentages = defaultdict(lambda: defaultdict(int))
            for block_id_key, tap_response_types in self.dv_correct_counts.items():
                block_total = 0
                for tap_response_type, count in tap_response_types.items():
                    block_total += count
                for tap_response_type, count in tap_response_types.items():
                    self.dv_correct_block_percentages[block_id_key][tap_response_type] = count / block_total

            # Calculate the CORRECT_GO/STOP session-level percentages
            dv_correct_session_counts = defaultdict(int)
            self.dv_correct_session_percentages = defaultdict(float)
            for block_id_key, tap_response_types in self.dv_correct_counts.items():
                for tap_response_type_key, item_count in tap_response_types.items():
                    dv_correct_session_counts[tap_response_type_key] += item_count
            correct_total = 0
            for tap_response_type_key, count in dv_correct_session_counts.items():
                correct_total += count
            for tap_response_type_key, count in dv_correct_session_counts.items():
                self.dv_correct_session_percentages[tap_response_type_key] = count / correct_total

            self.dv_correct_go_responses = list()
            self.dv_correct_stop_responses = list()
            self.dv_correct_responses = defaultdict(lambda: defaultdict(list))
            self.dv_incorrect_healthy_selected_responses = list()
            self.dv_incorrect_healthy_not_selected_responses = list()
            self.dv_incorrect_unhealthy_selected_responses = list()
            self.dv_incorrect_unhealthy_not_selected_responses = list()
            for session_event in session_events:
                # GO/STOP
                if 'tapResponseType' in session_event:
                    tap_response_type = session_event['tapResponseType']
                    tap_response_start = self.numericify(session_event['tapResponseStart'])
                    item_type = session_event['itemType']
                    self.dv_correct_responses[tap_response_type][item_type].append(tap_response_start)
                    if tap_response_type == 'CORRECT_GO':
                        self.dv_correct_go_responses.append(tap_response_start)
                    if tap_response_type == 'CORRECT_STOP':
                        self.dv_correct_stop_responses.append(tap_response_start)

                    trial_type = session_event['trialType']
                    selected = session_event['selected']
                    if trial_type == 'STOP' and tap_response_type != 'CORRECT_STOP':
                        if item_type == 'HEALTHY':
                            if selected != 'random':
                                self.dv_incorrect_healthy_selected_responses.append(tap_response_start)
                            if selected == 'random':
                                self.dv_incorrect_healthy_not_selected_responses.append(tap_response_start)
                        if item_type == 'NON_HEALTHY':
                            if selected != 'random':
                                self.dv_incorrect_unhealthy_selected_responses.append(tap_response_start)
                            if selected == 'random':
                                self.dv_incorrect_unhealthy_not_selected_responses.append(tap_response_start)

        calculate_durations()
        count_trial_and_types()
        count_raw_events()
        check_value_labels()
        self.check_points(row)
        calculate_dependent_variables()
        self.calculate_ssrt(row)

        def cell(row, column):
            return '{}{}'.format(str(row), str(column))

        A = 'A'
        B = 'B'
        C = 'C'
        D = 'D'
        E = 'E'
        F = 'F'
        G = 'G'
        H = 'H'
        I = 'I'
        J = 'J'
        letters = [A, B, C, D, E, F, G, H, I, J]
        wb = Workbook()

        # Counts
        print('TRIAL COUNT: ', self.trial_count)
        # Reuse the default sheet
        counts_sheet = wb.active
        counts_sheet.title = 'Counts'

        # Trial Counts
        counts_sheet[cell(A, 1)] = 'Trial Count'
        counts_sheet[cell(B, 1)] = self.trial_count

        print('\nRAW COUNTS:')
        print(' ON', self.raw_count['on'])
        r = 3
        counts_sheet[cell(A, r)] = 'Raw Counts'
        r += 1
        counts_sheet[cell(A, r)] = 'On'
        r += 1
        for key, value in self.raw_count['on'].items():
            counts_sheet[cell(A, r)] = key
            counts_sheet[cell(B, r)] = value
            r += 1
            print(key, value)

        print('OFF', self.raw_count['off'])
        r += 1
        counts_sheet[cell(A, r)] = 'Off'
        r += 1
        for key, value in self.raw_count['off'].items():
            counts_sheet[cell(A, r)] = key
            counts_sheet[cell(B, r)] = value
            r += 1
            print(key, value)

        # Durations
        print('\nTRIAL DURATIONS:')
        for key in self.durations:
            print(key, self.durations[key])

        print('\nTRIAL STATS:')
        pprint(self.trial_stats)
        r = 1
        stats_sheet = wb.create_sheet('Stats')
        stats_sheet[cell(A, r)] = 'Field'
        stats_sheet[cell(B, r)] = 'Min'
        stats_sheet[cell(C, r)] = 'Max'
        stats_sheet[cell(D, r)] = 'Mean'
        stats_sheet[cell(E, r)] = 'St Dev'
        r += 1
        for field, stats in self.trial_stats.items():
            stats_sheet[cell(A, r)] = field
            stats_sheet[cell(B, r)] = stats['min']
            stats_sheet[cell(C, r)] = stats['max']
            stats_sheet[cell(D, r)] = stats['mean']
            stats_sheet[cell(E, r)] = stats['stdev']
            r += 1

        # Trial Types
        # - Block
        r = 1
        trial_types_sheet = wb.create_sheet('Trial Types')
        trial_types_sheet[cell(A, r)] = 'Session'
        r += 1
        trial_types_sheet[cell(A, r)] = 'Trial Type'
        trial_types_sheet[cell(B, r)] = 'Count'
        trial_types_sheet[cell(C, r)] = 'Percentage'
        for trial_type in ['GO', 'STOP']:
            r += 1
            trial_types_sheet[cell(A, r)] = trial_type
            trial_types_sheet[cell(B, r)] = self.session_trial_type_counts[trial_type]
            trial_types_sheet[cell(C, r)] = self.session_trial_type_percentages[trial_type]
        # - Session
        r += 2
        trial_types_sheet[cell(A, r)] = 'Block'
        r += 1
        trial_types_sheet[cell(A, r)] = 'Block'
        trial_types_sheet[cell(B, r)] = 'Trial Type'
        trial_types_sheet[cell(C, r)] = 'Count'
        trial_types_sheet[cell(D, r)] = 'Percentage'
        for block_key in irange(1, 4):
            for trial_type in ['GO', 'STOP']:
                r += 1
                trial_types_sheet[cell(A, r)] = block_key
                trial_types_sheet[cell(B, r)] = trial_type
                trial_types_sheet[cell(C, r)] = self.block_trial_type_counts[block_key][trial_type]
                trial_types_sheet[cell(D, r)] = self.block_trial_type_percentages[block_key][trial_type]

        print('\nSESSION TRIAL TYPE COUNTS:')
        pprint(self.session_trial_type_counts)
        print('\nSESSION TRIAL TYPE PERCENTAGES:')
        pprint(self.session_trial_type_percentages)
        print('\nBLOCK TRIAL TYPE COUNTS:')
        pprint(self.block_trial_type_counts)
        print('\nBLOCK TRIAL TYPE PERCENTAGES:')
        pprint(self.block_trial_type_percentages)

        # Trial Items
        # - Block
        r = 1
        trial_types_sheet = wb.create_sheet('Item Types')
        trial_types_sheet[cell(A, r)] = 'Session'
        r += 1
        trial_types_sheet[cell(A, r)] = 'Item Type'
        trial_types_sheet[cell(B, r)] = 'Count'
        trial_types_sheet[cell(C, r)] = 'Percentage'
        for trial_type in ['HEALTHY', 'HEALTHY_RANDOM', 'HEALTHY_NOT_RANDOM', 'NON_HEALTHY']:
            r += 1
            trial_types_sheet[cell(A, r)] = trial_type
            trial_types_sheet[cell(B, r)] = self.session_item_type_counts[trial_type]
            trial_types_sheet[cell(C, r)] = self.session_item_type_percentages[trial_type]
        # - Session
        r += 2
        trial_types_sheet[cell(A, r)] = 'Block'
        r += 1
        trial_types_sheet[cell(A, r)] = 'Block'
        trial_types_sheet[cell(B, r)] = 'Item Type'
        trial_types_sheet[cell(C, r)] = 'Count'
        trial_types_sheet[cell(D, r)] = 'Percentage'
        for block_key in irange(1, 4):
            for trial_type in ['HEALTHY', 'HEALTHY_RANDOM', 'HEALTHY_NOT_RANDOM', 'NON_HEALTHY']:
                r += 1
                trial_types_sheet[cell(A, r)] = block_key
                trial_types_sheet[cell(B, r)] = trial_type
                trial_types_sheet[cell(C, r)] = self.block_item_type_counts[block_key][trial_type]
                trial_types_sheet[cell(D, r)] = self.block_item_type_percentages[block_key][trial_type]
        print('\nSESSION ITEM TYPE COUNTS:')
        pprint(self.session_item_type_counts)
        print('\nSESSION ITEM TYPE PERCENTAGES:')
        pprint(self.session_item_type_percentages)
        print('\nBLOCK ITEM TYPE COUNTS:')
        pprint(self.block_item_type_counts)
        print('\nBLOCK ITEM TYPE PERCENTAGES:')
        pprint(self.block_item_type_percentages)

        r = 1
        raw_round_sheet = wb.create_sheet('Raw Rounds')
        raw_round_sheet[cell(A, r)] = 'Round'
        raw_round_sheet[cell(B, r)] = 'Count'
        r += 1
        for block_key in irange(1, 4):
            raw_round_sheet[cell(A, r)] = block_key
            raw_round_sheet[cell(B, r)] = len(self.raw_round_trial_counts[block_key])
            r += 1
        print('\nRAW ROUND TRIAL COUNTS:')
        for key in self.raw_round_trial_counts:
            print(key, len(self.raw_round_trial_counts[key]), self.raw_round_trial_counts[key])

        # Label Allocation Counts
        r = 1
        label_allocation_count_sheet = wb.create_sheet('Label Allocations')
        label_allocation_count_sheet[cell(A, r)] = 'Session'
        r += 1
        label_allocation_count_sheet[cell(A, r)] = 'Trial Type'
        label_allocation_count_sheet[cell(B, r)] = 'Prefix'
        label_allocation_count_sheet[cell(C, r)] = 'Count'
        label_allocation_count_sheet[cell(D, r)] = 'Percentage'
        for item_type in ['HEALTHY', 'NON_HEALTHY']:
            for prefix in ['1_', '2_']:
                r += 1
                label_allocation_count_sheet[cell(A, r)] = item_type
                label_allocation_count_sheet[cell(B, r)] = prefix
                label_allocation_count_sheet[cell(C, r)] = self.label_allocation_counts[item_type][prefix]
                label_allocation_count_sheet[cell(D, r)] = self.label_allocation_item_id_percentages[item_type][prefix]
        print('\nLABEL ALLOCATION COUNTS:')
        pprint(self.label_allocation_counts)

        # Label Allocation Percentages
        print('\nLABEL ALLOCATION PERCENTAGES:')
        pprint(self.label_allocation_item_id_percentages)
        pprint(self.label_allocation_item_type_percentages)

        r += 2
        label_allocation_count_sheet[cell(A, r)] = 'Item Type'
        label_allocation_count_sheet[cell(B, r)] = 'Percentage'
        r += 1
        for item_type in self.label_allocation_item_type_percentages:
            label_allocation_count_sheet[cell(A, r)] = item_type
            label_allocation_count_sheet[cell(B, r)] = self.label_allocation_item_type_percentages[item_type]
            r += 1

        # Selected Item IDs
        r = 1
        selected_items_sheet = wb.create_sheet('Selected Items')
        for index, selected_label in enumerate(self.selected_item_ids):
            selected_items_sheet[cell(letters[index], r)] = selected_label
        r += 1
        for index, selected_label in enumerate(self.selected_item_ids):
            for i, selected_item_id in enumerate(self.selected_item_ids[selected_label]):
                selected_items_sheet[cell(letters[index], r+i)] = selected_item_id
        print('\nSELCTED ITEM IDs:')
        print(self.selected_item_ids)

        # Unique Item IDs
        # - Session
        r = 1
        unique_items_sheet = wb.create_sheet('Unique Items - Session')
        unique_items_sheet[cell(A, r)] = 'Session'
        r += 1
        for index, unique_item_id in enumerate(self.session_item_ids):
            unique_items_sheet[cell(A, r+index)] = unique_item_id
        # - Blocks
        r = 1
        unique_items_sheet = wb.create_sheet('Unique Items - Blocks')
        for block_key in irange(1, 4):
            unique_items_sheet[cell(letters[block_key-1], r)] = block_key
        r += 1
        for block_key in irange(1, 4):
            for index, unique_item_id in enumerate(self.block_item_ids[block_key]):
                unique_items_sheet[cell(letters[block_key-1], r+index)] = unique_item_id

        print('\nSESSION ITEM IDs:')
        print(self.session_item_ids)
        print('\nBLOCK ITEM IDs:')
        pprint(self.block_item_ids)

        r = 1
        correct_count_sheet = wb.create_sheet('Correct Counts')
        correct_count_sheet[cell(A, r)] = 'Block'
        r += 1
        correct_count_sheet[cell(A, r)] = 'Block'
        correct_count_sheet[cell(B, r)] = 'Trial Type'
        correct_count_sheet[cell(C, r)] = 'Count'
        correct_count_sheet[cell(C, r)] = 'Count'
        r += 1
        for block_key in irange(1, 4):
            for trial_type in ['CORRECT_GO', 'CORRECT_STOP']:
                correct_count_sheet[cell(A, r)] = block_key
                correct_count_sheet[cell(B, r)] = trial_type
                correct_count_sheet[cell(C, r)] = self.dv_correct_counts[block_key][trial_type]
                r += 1


        print('\nDV CORRECT COUNTS:')
        pprint(self.dv_correct_counts)
        print('DV BLOCK LEVEL CORRECT PERCENTAGES:')
        pprint(self.dv_correct_block_percentages)
        print('DV SESSION LEVEL CORRECT PERCENTAGES:')
        pprint(self.dv_correct_session_percentages)
        # assert False

        print('mean CORRECT_GO responses', self.mean(self.dv_correct_go_responses))
        print('mean CORRECT_GO HEALTHY responses', self.mean(self.dv_correct_responses['CORRECT_GO']['HEALTHY']))
        print('mean CORRECT_GO UNHEALTHY responses', self.mean(self.dv_correct_responses['CORRECT_GO']['NON_HEALTHY']))
        print('mean CORRECT_STOP responses', self.mean(self.dv_correct_stop_responses))
        print('mean CORRECT_STOP HEALTHY responses', self.mean(self.dv_correct_responses['CORRECT_STOP']['HEALTHY']))
        print('mean CORRECT_STOP UNHEALTHY responses', self.mean(self.dv_correct_responses['CORRECT_STOP']['NON_HEALTHY']))

        print('mean INCORRECT HEALTHY SELECTED responses', self.mean(self.dv_incorrect_healthy_selected_responses))
        print('mean INCORRECT HEALTHY NOT SELECTED responses', self.mean(self.dv_incorrect_healthy_not_selected_responses))
        print('mean INCORRECT UNHEALTHY SELECTED responses', self.mean(self.dv_incorrect_unhealthy_selected_responses))
        print('mean INCORRECT UNHEALTHY NOT SELECTED responses', self.mean(self.dv_incorrect_unhealthy_not_selected_responses))

        excel_filename = 'DerivedValues.xlsx'
        wb.save(excel_filename)
        # assert False
        # print('\nLog')

        self.session_event_log.print()


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

    # def log_message_if_check_failed(self, check_passed, session_event, extra_message=None):
    #     if not check_passed:
    #         extra = ''
    #         if extra_message:
    #             extra = ': {}'.format(extra_message)
    #         message = 'Check failed: {} {} {} gameSessionID={} roundID={}, trialID={}{}'.format(
    #             session_event['trialType'], session_event['initialTapResponseType'], session_event['secondTapResponseType'],
    #             session_event['gameSessionID'], session_event['roundID'], session_event['trialID'], extra)
    #         self.log_message(message, session_event)

    def check_points(self, row):
        running_total = 0
        session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
        for session_event in session_events:

            trial_type = session_event['trialType']
            initial_tap_response_type = session_event['initialTapResponseType']
            second_tap_response_type = session_event['secondTapResponseType']
            points_this_trial = session_event['pointsThisTrial']

            if trial_type == 'GO':
                if initial_tap_response_type == 'CORRECT_GO' and second_tap_response_type == 'N/A':
                    check_passed = points_this_trial == 20
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                elif initial_tap_response_type == 'INCORRECT_GO' and second_tap_response_type == 'N/A':
                    check_passed = points_this_trial == -20
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                else:
                    # print(initial_tap_response_type, second_tap_response_type)
                    check_passed = points_this_trial == -50
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
            if trial_type == 'DOUBLE':
                if initial_tap_response_type == 'CORRECT' and second_tap_response_type == 'CORRECT':
                    check_passed = points_this_trial == 50
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                else:
                    check_passed = points_this_trial == -50
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)

            running_total += points_this_trial
            points_running_total = session_event['pointsRunningTotal']

            check_passed = points_running_total == running_total
            self.session_event_log.log_message_if_check_failed(check_passed, session_event, extra_message='points_running_total != running_total')

    def check_tap_responses(self, row):
        session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
        for session_event in session_events:
            trial_type = session_event['trialType']

            initial_tap_response_type = session_event['initialTapResponseType']
            second_tap_response_type = session_event['initialTapResponseType']

            initial_tap_response_start = self.numericify(session_event['initialTapResponseStart'])
            if trial_type == 'GO':
                if initial_tap_response_type == 'CORRECT_GO':
                    check_passed = initial_tap_response_start > 0 and self.within_stimulus_boundaries(session_event, prefix='initialTapResponsePosition')
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if initial_tap_response_type == 'INCORRECT_GO':
                    check_passed = initial_tap_response_start == 0
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if initial_tap_response_type == 'MISS_GO':
                    check_passed = initial_tap_response_start > 0 and not self.within_stimulus_boundaries(session_event, prefix='initialTapResponsePosition')
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)

            if trial_type == 'DOUBLE':
                if initial_tap_response_type == 'CORRECT_GO':
                    check_passed = initial_tap_response_start == 0
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if initial_tap_response_type == 'INCORRECT_GO':
                    check_passed = initial_tap_response_start > 0 and self.within_stimulus_boundaries(session_event, prefix='initialTapResponsePosition')
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if initial_tap_response_type == 'MISS_STOP':
                    check_passed = initial_tap_response_start > 0 and not self.within_stimulus_boundaries(session_event, prefix='initialTapResponsePosition')
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)

            second_tap_response_start = self.numericify(session_event['initialTapResponseStart'])
            if trial_type == 'GO':
                if second_tap_response_type == 'N/A':
                    check_passed = second_tap_response_start = 0
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if second_tap_response_type == 'INCORRECT_DOUBLE_GO':
                    check_passed = second_tap_response_start > 0 and self.within_stimulus_boundaries(session_event, prefix='initialTapResponsePosition')
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if second_tap_response_type == 'MISS_GO':
                    check_passed = second_tap_response_start > 0 and not self.within_stimulus_boundaries(session_event, prefix='initialTapResponsePosition')
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)

            if trial_type == 'DOUBLE':
                if second_tap_response_type == 'CORRECT':
                    check_passed = second_tap_response_start > 0 and self.within_stimulus_boundaries(session_event, prefix='initialTapResponsePosition')
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if second_tap_response_type == 'INCORRECT':
                    check_passed = second_tap_response_start == 0
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)
                if second_tap_response_type == 'MISS':
                    check_passed = second_tap_response_start > 0 and not self.within_stimulus_boundaries(session_event, prefix='initialTapResponsePosition')
                    self.session_event_log.log_message_if_check_failed(check_passed, session_event)

    def calculate_ssrt(self, row):
        pass

    def calculate(self, row):
        super(DoubleDataExtractor, self).calculate(row)
