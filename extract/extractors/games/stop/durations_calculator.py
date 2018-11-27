import statistics
from collections import defaultdict

from .abstract_stop_evaluator import AbstractStopEvaluator

from utils import get_session_events, get_keypath_value, remove_none_values


class DurationsCalculator(AbstractStopEvaluator):

    def __init__(self):
        self.session_duration = 0
        self.durations = defaultdict(list)

    def evaluate(self, row):
        self.calculate_durations(row)

    def calculate_durations(self, row):

        def calculate_session_duration():
            session_start = get_keypath_value(row, 'data.0.sessionStart')
            session_end = get_keypath_value(row, 'data.0.sessionEnd')
            self.session_duration = session_start - session_end

        def record_duration(key, value):
            self.durations[key].append(value)

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
