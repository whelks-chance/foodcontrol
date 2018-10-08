import os
import json
import pprint
import requests

from settings import CKAN_API_URL, CKAN_API_KEY, CSV_PATH


def create_or_update_ckan_dataset(dataset_dict):
    url = CKAN_API_URL + '/action/package_create'
    data = json.dumps(dataset_dict).encode('utf-8')
    headers = {
        'Authorization': CKAN_API_KEY,
        'content-type': 'application/json',
    }
    response = requests.post(url, data=data, headers=headers)
    response_dict = response.json()
    if response_dict['success'] is False:
        if response.reason == 'CONFLICT':
            url = CKAN_API_URL + '/action/package_update'
            response = requests.post(url, data=data, headers=headers)
            response_dict = response.json()
    assert response.status_code == 200
    assert response_dict['success'] is True
    created_dataset = response_dict['result']
    return created_dataset


def add_ckan_resource(dataset_name, resource_name, resource_path):
    resource_dict = {
        'name': resource_name,
        'package_id': dataset_name,
        'mimetype': 'text/csv',
    }
    url = CKAN_API_URL + '/action/resource_create'
    data = resource_dict
    headers = {
        'Authorization': CKAN_API_KEY,
    }
    files = [('upload', open(resource_path, 'r', encoding='utf-8'))]
    response = requests.post(url, data=data, headers=headers, files=files)
    response_dict = response.json()
    created_resource = response_dict['result']
    return created_resource


def create_dataset(dataset_path, dataset_name):
    print('CREATE CKAN DATASET: {}'.format(dataset_path))
    description = 'The description for {}'.format(dataset_name)
    owner_organization = 'cubric-food-control'
    dataset_dict = {
        'name': dataset_name,
        'notes': description,
        'owner_org': owner_organization,
    }
    created_dataset = create_or_update_ckan_dataset(dataset_dict)
    # pprint.pprint(created_dataset)
    csv_filenames = os.listdir(dataset_path)
    for csv_filename in csv_filenames:
        resource_path = dataset_path / csv_filename
        print('\tADD CKAN RESOURCE: {}'.format(resource_path))
        resource_name = csv_filename.split('.')[0]
        add_ckan_resource(dataset_name, resource_name, resource_path)


filenames = os.listdir(CSV_PATH)
for filename in filenames:
    create_dataset(CSV_PATH / filename, filename)
