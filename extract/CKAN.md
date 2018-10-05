# CKAN


## Clean and Initialize

https://docs.ckan.org/en/2.8/maintaining/database-management.html#initialization

```bash
paster db clean -c /etc/ckan/default/development.ini
paster db init -c /etc/ckan/default/development.ini
```


## Create Test Data

https://docs.ckan.org/en/2.8/maintaining/getting-started.html#creating-test-data

```bash
paster create-test-data -c /etc/ckan/default/development.ini
```

## DataStore

https://docs.ckan.org/en/2.8/maintaining/datastore.html#setting-up-the-datastore

Create postgres user and database:

```bash
sudo -u postgres createuser -S -D -R -P -l datastore_default
sudo -u postgres createdb -O ckan_default datastore_default -E utf-8
```

Update datastore URLs in CKAN config file:

```bash
ckan.datastore.write_url = postgresql://ckan_default:pass@localhost/datastore_default
ckan.datastore.read_url = postgresql://datastore_default:pass@localhost/datastore_default
```

Add plugin to config file:

```bash
ckan.plugins = datastore
```

Set DB permissions:

```bash
sudo ckan datastore set-permissions | sudo -u postgres psql --set ON_ERROR_STOP=1
```

Test by retrieving a JSON object:

```bash
curl -X GET "http://127.0.0.1:5000/api/3/action/datastore_search?resource_id=_table_metadata"
```


## Serve

```bash
. /usr/lib/ckan/default/bin/activate
cd /usr/lib/ckan/default/src/ckan
paster serve /etc/ckan/default/development.ini
```


## Add a Sysadmin User

```bash
paster sysadmin add USERNAME email=USERNAME@localhost name=USERNAME -c /etc/ckan/default/development.ini
```


## Make a CKAN User a Sysadmin

Required for creating organizations and datasets.

```bash
paster sysadmin add CKANUSERNAME -c /etc/ckan/default/development.ini
```


## Make FileStore Location Writable

```bash
/var/lib/ckan
```


## Start the DataPusher

```bash
python datapusher/main.py deployment/datapusher_settings.py
```

