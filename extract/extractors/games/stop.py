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

    session_duration = 0
    durations = defaultdict(list)
    trial_type_count = defaultdict(int)
    item_type_count = defaultdict(lambda: defaultdict(int))
    raw_count = {
        'on': defaultdict(int),
        'off': defaultdict(int)
    }
    logs = []

    def log_message(self, message, data=None):
        log = {
            'message': message,
            'data': data
        }
        pprint(log)
        self.logs.append(log)

    def log_message_if_check_fails(self, check_passes, trial, response, session_event):
        if not check_passes:
            message = 'Check failed: {} {} gameSessionID={} roundID={}, trialID={}'.format(
                                trial, response,
                                session_event['gameSessionID'], session_event['roundID'], session_event['trialID'])
            self.log_message(message, session_event)

    def clear(self):
        self.session_duration = 0
        self.durations.clear()
        self.trial_type_count.clear()
        self.item_type_count.clear()
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
            pprint(session_event)
            trial_type = session_event['trialType']
            tap_response_type = session_event['tapResponseType']
            if trial_type == 'GO':
                print('check_tap_responses: GO')
                tap_response_start = self.numericify(session_event['tapResponseStart'])
                if tap_response_type == 'CORRECT_GO':
                    check_passes = tap_response_start > 0 and self.within_stimulus_boundaries(session_event)
                    self.log_message_if_check_fails(check_passes, 'GO', 'CORRECT_GO', session_event)
                if tap_response_type == 'INCORRECT_GO':
                    check_passes = tap_response_start == 0
                    self.log_message_if_check_fails(check_passes, 'GO', 'INCORRECT_GO', session_event)
                if tap_response_type == 'MISS_GO':
                    check_passes = tap_response_start > 0 and not self.within_stimulus_boundaries(session_event)
                    self.log_message_if_check_fails(check_passes, 'GO', 'MISS_GO', session_event)

            if trial_type == 'STOP':
                print('check_tap_responses: STOP')
                if tap_response_type == 'CORRECT_GO':
                    check_passes = session_event['tapResponseStart'] == 0
                    self.log_message_if_check_fails(check_passes, 'STOP', 'CORRECT_GO', session_event)
                if tap_response_type == 'INCORRECT_GO':
                    check_passes = session_event['tapResponseStart'] > 0 and self.within_stimulus_boundaries(session_event)
                    self.log_message_if_check_fails(check_passes, 'STOP', 'INCORRECT_GO', session_event)
                if tap_response_type == 'MISS_STOP':
                    check_passes = session_event['tapResponseStart'] > 0 and not self.within_stimulus_boundaries(session_event)
                    self.log_message_if_check_fails(check_passes, 'STOP', 'MISS_STOP', session_event)

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
                    'inter_trial'
                ]

                self.trial_stats = {}
                for trial_category in trial_categories:
                    self.trial_stats[trial_category] = calculate_stats(trial_category)

            calculate_session_duration()
            calculate_trial_durations()
            calculate_trial_duration_stats()

        def count_trial_types():
            session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
            for session_event in session_events:
                # trialType = GO/STOP
                self.trial_type_count[session_event['trialType']] += 1
                # itemType = HEALTHY/NON-HEALTHY
                item_type = session_event['itemType']
                selected = session_event['selected']
                block_id = session_event['roundID']
                if item_type == 'HEALTHY':
                    self.item_type_count[block_id]['HEALTHY'] += 1
                    if selected == 'RANDOM':
                        self.item_type_count[block_id]['HEALTHY_RANDOM'] += 1
                    else:
                        self.item_type_count[block_id]['HEALTHY_NOT_RANDOM'] += 1
                if item_type == 'NON_HEALTHY':
                    self.item_type_count[block_id]['NON_HEALTHY'] += 1

        def count_raw_events():
            # "Raw data"
            raw_events = self.get_keypath_value(row, 'data.0.rawEvents')
            for raw_event in raw_events:
                self.raw_count['on'][raw_event['eventOn']] += 1
                self.raw_count['off'][raw_event['eventOff']] += 1

        calculate_durations()
        count_trial_types()
        count_raw_events()

        print('\nDurations:')
        print(' ON', self.raw_count['on'])
        print('OFF', self.raw_count['off'])
        pprint(self.trial_stats)
        for key in self.durations:
            print(key, self.durations[key])
        for key in self.trial_type_count:
            print(key, self.trial_type_count[key])

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
