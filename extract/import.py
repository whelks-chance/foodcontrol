import os
import csv
import json
import pprint
from urllib.request import urlopen, Request
from urllib.error import HTTPError

from pathlib import Path

from settings import CKAN_API_URL, CKAN_API_KEY

csv_path = Path('./CSV')
# csv_path = csv_path / '200818'


def create_ckan_resource(resource_path, resource_name):
    print('\tCREATE CKAN RESOURCE: {}'.format(resource_path))
    with open(resource_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        csv_content = list(csv_reader)
    print(csv_content)


def create_ckan_dataset(dataset_path, dataset_name):
    print('CREATE CKAN DATASET: {}'.format(dataset_path))
    csv_filenames = os.listdir(dataset_path)
    for csv_filename in csv_filenames:
        create_ckan_resource(dataset_path / csv_filename, csv_filename)


# filenames = os.listdir(csv_path)
# for filename in filenames:
#     create_ckan_dataset(csv_path / filename, filename)


headers = {
    'Authorization': CKAN_API_KEY,
    'content-type': 'application/json',
}
url = CKAN_API_URL + '/action/organization_list'
request = Request(url, headers=headers)
response = urlopen(request)
assert response.code == 200
response_dict = json.loads(response.read())
assert response_dict['success'] is True
pprint.pprint(response_dict)


def create_or_update_dataset(dataset_dict):
    data = json.dumps(dataset_dict).encode('utf-8')
    headers = {
        'Authorization': CKAN_API_KEY,
        'content-type': 'application/json',
    }
    try:
        url = CKAN_API_URL + '/action/package_create'
        request = Request(url, data=data, headers=headers)
        response = urlopen(request)
    except HTTPError as e:
        if e.reason == 'CONFLICT':
            url = CKAN_API_URL + '/action/package_update'
            request = Request(url, data=data, headers=headers)
            response = urlopen(request)
    finally:
        assert response.code == 200
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True
        created_dataset = response_dict['result']
        return created_dataset


dataset_name = 'my-dataset-1'
description = 'The description for {}'.format(dataset_name)
owner_organization = 'cubric-food-control'
dataset_dict = {
    'name': dataset_name,
    'notes': description,
    'owner_org': owner_organization,
}
created_dataset = create_or_update_dataset(dataset_dict)
pprint.pprint(created_dataset)


def add_resource(resource_dict, resource_path):
    data = json.dumps(resource_dict).encode('utf-8')
    headers = {
        'Authorization': CKAN_API_KEY,
        'content-type': 'application/json',
    }
    try:
        url = CKAN_API_URL + '/action/resource_create'
        files = [('upload', open(resource_path, 'r', encoding='utf-8'))]
        request = Request(url, data=data, headers=headers, files=files)
        response = urlopen(request)
    except HTTPError as e:
        print(e)

# resource_name = 'MCII Game'
# resource_path = csv_path / Path('200818') / 'MCII.csv'
# resource_dict = {
#     'name': resource_name,
#     'package_id': dataset_name,
#     'mimetype': 'text/csv',
# }
# pprint.pprint(resource_dict)
# print(resource_path)
# add_resource(resource_dict, resource_path)
