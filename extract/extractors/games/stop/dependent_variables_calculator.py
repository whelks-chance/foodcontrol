from collections import defaultdict


class DependentVariablesCalculator:

    def __init__(self):
        self.dv_correct_counts = None
        self.dv_correct_block_percentages = None
        self.dv_correct_session_percentages = None
        self.dv_correct_go_responses = None
        self.dv_correct_stop_responses = None
        self.dv_correct_responses = None
        self.dv_incorrect_healthy_selected_responses = None
        self.dv_incorrect_healthy_not_selected_responses = None
        self.dv_incorrect_unhealthy_selected_responses = None
        self.dv_incorrect_unhealthy_not_selected_responses = None

    def calculate_dependent_variables(self, row):
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