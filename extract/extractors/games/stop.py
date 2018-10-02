from collections import defaultdict

from .gamedataextractor import GameDataExtractor


class AbstractStopDataExtractor(GameDataExtractor):
    """The abstract base class for all STOP games"""

    @staticmethod
    def get_value_keypaths():
        return [
            ('data.captureDate', 'Capture Date'),
        ]

    durations = defaultdict(list)
    trial_type_count = defaultdict(int)
    item_type_count = defaultdict(lambda: defaultdict(int))
    raw_count = {
        'on': defaultdict(int),
        'off': defaultdict(int)
    }

    def clear(self):
        self.durations.clear()
        self.trial_type_count.clear()
        self.item_type_count.clear()
        self.raw_count['on'].clear()
        self.raw_count['off'].clear()

    def check(self, row):
        super(AbstractStopDataExtractor, self).check(row)

        def check_trials_count():
            number_of_rounds = 4
            number_of_trials = 48
            session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
            assert len(session_events) == number_of_rounds * number_of_trials

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

    def calculate(self, row):
        super(AbstractStopDataExtractor, self).calculate(row)

        def calculate_durations():

            def calculate_session_duration():
                # Game play duration: sessionEnd - sessionStart
                session_start = self.get_keypath_value(row, 'data.0.sessionStart')
                session_end = self.get_keypath_value(row, 'data.0.sessionEnd')
                session_duration = session_start - session_end
                # TODO: Record session_duration

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
                session_events = get_session_events(row)
                if session_events:
                    previous_session_event = None
                    for session_event in session_events:
                        trial_start = session_event['trialStart']
                        trial_end = session_event['trialEnd']
                        trial_duration = trial_end - trial_start
                        record_duration('trial', trial_duration)

                        stop_signal_duration = None
                        stop_signal_onset = session_event['stopSignalOnset']
                        stop_signal_offset = session_event['stopSignalOffset']
                        if stop_signal_onset and stop_signal_offset:
                            stop_signal_duration = stop_signal_offset - stop_signal_onset
                        record_duration('stop_signal', stop_signal_duration)

                        stimulus_duration = None
                        stimulus_onset = session_event['stimulusOnset']
                        stimulus_offset = session_event['stimulusOffset']
                        if stimulus_onset and stimulus_offset:
                            stimulus_duration = stimulus_offset - stimulus_onset
                        record_duration('stimulus', stimulus_duration)

                        signal_stop_difference = None  # Difference between signal onset and stop signal delay
                        stop_signal_delay = session_event['stopSignalDelay']
                        if stop_signal_onset and stop_signal_delay:
                            signal_stop_difference = stop_signal_onset - stop_signal_delay
                        record_duration('signal_stop_difference', signal_stop_difference)

                        stimulus_stop_difference = None  # Duration between signal offset and stimulus offset
                        if stimulus_offset and stop_signal_offset:
                            stimulus_stop_difference = stimulus_offset - stop_signal_offset
                        record_duration('stimulus_stop_difference', stimulus_stop_difference)

                        inter_trial_duration = None
                        if previous_session_event:
                            previous_trial_start = previous_session_event['trialStart']
                            inter_trial_duration = trial_start - previous_trial_start
                        record_duration('inter_trial', inter_trial_duration)

                        previous_session_event = session_event

            calculate_session_duration()
            calculate_trial_durations()

        def count_raw_events():
            # raw_events = self.value(row, 'data.0.rawEvents')
            raw_events = self.get_keypath_value(row, 'data.0.rawEvents')
            for raw_event in raw_events:
                self.raw_count['on'][raw_event['eventOn']] += 1
                self.raw_count['off'][raw_event['eventOff']] += 1

        def count_trial_types():
            session_events = self.get_keypath_value(row, 'data.0.sessionEvents')
            for session_event in session_events:
                self.trial_type_count[session_event['trialType']] += 1
                itemType = session_event['itemType']
                selected = session_event['selected']
                blockID = session_event['roundID']
                if itemType == 'HEALTHY':
                    self.item_type_count[blockID]['HEALTHY'] += 1
                    if selected == 'RANDOM':
                        self.item_type_count[blockID]['HEALTHY_RANDOM'] += 1
                    else:
                        self.item_type_count[blockID]['HEALTHY_NOT_RANDOM'] += 1
                if itemType == 'NON_HEALTHY':
                    self.item_type_count[blockID]['NON_HEALTHY'] += 1

        calculate_durations()
        count_raw_events()
        count_trial_types()

        print(self.raw_count['on'])
        print(self.raw_count['off'])
        for key in self.durations:
            print(key, self.durations[key])
        for key in self.trial_type_count:
            print(key, self.trial_type_count[key])
        for key in self.item_type_count:
            print(key, self.item_type_count[key])


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
