import json
import pprint
import csv

import os


class Eligibility:
    def __init__(self, row):
        self.data = row['data']

    def fields(self):
        return [

            "gender",
            "dob",
            "bmi",
            "age",
            "eligible",
            "height_cm",
            "weight_kgs"
        ]

    def complex_fields(self):
        return [
            "height_unit1_val",
            "height_unit2_val",
            "height_units",

            "weight_unit1_val",
            "weight_unit2_val",
            "weight_units",

            "diet_no_specific_diet",
            "diet_vegetarian",
            "diet_vegan",
            "diet_raw_vegan",
            "diet_pescatarian",
            "diet_fruitarian",
            "diet_halal",
            "diet_kosher",
            "diet_other",

            "allergies_eggs",
            "allergies_milk",
            "allergies_fish",
            "allergies_shelfish",
            "allergies_tree_nuts",
            "allergies_peanuts",
            "allergies_wheat",
            "allergies_soy",
            "allergies_other",

            # TODO add these
            "eating_disorder",
            "eating_disorder_other"
        ]



    def height_unit1_val(self):
        return self.data['height']['unit1_val']

    def height_unit2_val(self):
        return self.data['height']['unit2_val']

    def height_units(self):
        return self.data['height']['units']


    def weight_unit1_val(self):
        return self.data['weight']['unit1_val']

    def weight_unit2_val(self):
        return self.data['weight']['unit2_val']

    def weight_units(self):
        return self.data['weight']['units']

    # Diet
    def diet_no_specific_diet(self):
        return 'No specific diet' in self.data['diet']

    def diet_vegetarian(self):
        return 'vegetarian' in self.data['diet']

    def diet_vegan(self):
        return 'vegan' in self.data['diet']

    def diet_raw_vegan(self):
        return 'raw_vegan' in self.data['diet']

    def diet_pescatarian(self):
        return 'Pescetarian' in self.data['diet']

    def diet_fruitarian(self):
        return 'fruitarian' in self.data['diet']

    def diet_halal(self):
        return 'halal' in self.data['diet']

    def diet_kosher(self):
        return 'kosher' in self.data['diet']

    def diet_other(self):
        return 'other' in self.data['diet']

    # Allergies
    def allergies_eggs(self):
        return 'eggs' in self.data['allergies']

    def allergies_milk(self):
        return 'milk' in self.data['allergies']

    def allergies_fish(self):
        return 'fish' in self.data['allergies']

    def allergies_shelfish(self):
        return 'shelfish' in self.data['allergies']

    def allergies_tree_nuts(self):
        return 'tree_nuts' in self.data['allergies']

    def allergies_peanuts(self):
        return 'peanuts' in self.data['allergies']

    def allergies_wheat(self):
        return 'wheat' in self.data['allergies']

    def allergies_soy(self):
        return 'soy' in self.data['allergies']

    def allergies_other(self):
        return 'other' in self.data['allergies']

        # TODO add these
    def eating_disorder(self):
        return self.data['eating-disorder']

    def eating_disorder_other(self):
        return self.data.get('eating-disorder-other', None)

    def get_complex_fields(self):
        cfs = []
        for cf in self.complex_fields():

            print(getattr(self, cf)())

            cfs.append(getattr(self, cf)())
        return cfs

    def write_csv(self):

        fields = []


        for f in self.fields():
            if f in self.data.keys():
                fields.append(self.data[f])
            else:
                fields.append(None)

        fields.extend(self.get_complex_fields())

        if os.path.isfile('eligibility.csv'):
            pass
        else:
            headers = []
            headers.extend(self.fields())
            headers.extend(self.complex_fields())

            with open('eligibility.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(headers)

        with open('eligibility.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)


class ReadRaw:
    def __init__(self):
        self.users = {}

    def open_file(self, filename):
        with open(filename, 'r') as file_handle:
            json_raw = json.load(file_handle)

            # print(pprint.pformat(json_raw))

            for row in json_raw:
                # print(pprint.pformat(row))

                if 'data' in row:

                    data_event = {}
                    data = row['data']
                    print('User ID', row['userId'])
                    print('Capture Date', row['captureDate'])

                    if 'bmi' in row['data']:
                        print('BMI', data['bmi'])
                        data_event['bmi'] = data['bmi']
                    if 'weight_kgs' in row['data']:
                        print('Weight KGs', data['weight_kgs'])
                        data_event['weight_kgs'] = data['weight_kgs']

                    if len(data_event.keys()):
                        if 'captureDate' in row:
                            print('BMI', row['captureDate'])
                            data_event['captureDate'] = row['captureDate']

                        if row['userId'] in self.users:
                            self.users[row['userId']].append(data_event)
                        else:
                            self.users[row['userId']] = [data_event]

                    # print(pprint.pformat(data))
                    print('\n')

        print(pprint.pformat(self.users))

        feedback = []

        for user in self.users.keys():
            individual_feedback = {}

            user_data = self.users[user]

            initial_bmi = float(user_data[0]['bmi'])
            recent_bmi = float(user_data[-1]['bmi'])

            print('User {} had Initial BMI of {}, now has {}'.format(user, initial_bmi, recent_bmi))
            individual_feedback['comment'] ='User {} had Initial BMI of {}, now has {}'.format(
                user, initial_bmi, recent_bmi
            )

            upper = initial_bmi * 1.1
            lower = initial_bmi * 0.9
            if recent_bmi < lower:
                print('Unhealthy user - too much weight loss')
                individual_feedback['error'] = 'Unhealthy user - too much weight loss'
            elif recent_bmi > upper:
                print('Unhealthy user - too much weight gain')
                individual_feedback['error'] = 'Unhealthy user - too much weight gain'
            else:
                print('User is within 10% of initial BMI')
                individual_feedback['ok'] = 'User is within 10% of initial BMI'

            print('\n')
            feedback.append(individual_feedback)

        return self.users, feedback

    def eligibility(self, filename):
        with open(filename, 'r') as file_handle:
            json_raw = json.load(file_handle)

            for row in json_raw:
                if row['type'] == 'eligibility':
                    el = Eligibility(row)
                    el.write_csv()


if __name__ == '__main__':
    rr = ReadRaw()

    filename = '../../091117.json'
    rr.eligibility(filename=filename)
    rr.open_file(filename=filename)

