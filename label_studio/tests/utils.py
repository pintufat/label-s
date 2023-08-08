"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import ujson as json

import json  # type: ignore[no-redef]
import re
import io
import pytest
import requests_mock  # type: ignore[import]
import requests
import tempfile
import os.path

from contextlib import contextmanager
from unittest import mock
from types import SimpleNamespace
from box import Box
from pathlib import Path

from django.test import Client
from django.apps import apps
from projects.models import Project
from ml.models import MLBackend
from tasks.serializers import TaskWithAnnotationsSerializer
from organizations.models import Organization
from users.models import User
from data_export.models import Export, ConvertedFormat
from django.conf import settings

try:
    from businesses.models import Business, BillingPlan  # type: ignore[import]
except ImportError:
    BillingPlan = Business = None


@contextmanager
def ml_backend_mock(**kwargs):  # type: ignore[no-untyped-def]
    with requests_mock.Mocker(real_http=True) as m:
        yield register_ml_backend_mock(m, **kwargs)  # type: ignore[no-untyped-call]


def register_ml_backend_mock(m, url='http://localhost:9090', predictions=None, health_connect_timeout=False, train_job_id='123', setup_model_version='abc'):  # type: ignore[no-untyped-def]
    m.post(f'{url}/setup', text=json.dumps({'status': 'ok', 'model_version': setup_model_version}))
    if health_connect_timeout:
        m.get(f'{url}/health', exc=requests.exceptions.ConnectTimeout)
    else:
        m.get(f'{url}/health', text=json.dumps({'status': 'UP'}))
    m.post(f'{url}/train', text=json.dumps({'status': 'ok', 'job_id': train_job_id}))
    m.post(f'{url}/predict', text=json.dumps(predictions or {}))
    m.post(f'{url}/webhook', text=json.dumps({}))
    m.get(f'{url}/versions', text=json.dumps({'versions': ["1", "2"]}))
    return m


@contextmanager
def import_from_url_mock(**kwargs):  # type: ignore[no-untyped-def]
    with mock.patch('data_import.uploader.validate_upload_url'):
        with requests_mock.Mocker(real_http=True) as m:
            url='https://data.heartextest.net'

            with open('./tests/test_suites/samples/test_1.csv', 'rb') as f:
                matcher = re.compile('data\.heartextest\.net/test_1\.csv')

                m.get(matcher, body=f, headers={'Content-Length': '100'})
                yield m


class _TestJob(object):
    def __init__(self, job_id):  # type: ignore[no-untyped-def]
        self.id = job_id


@contextmanager
def email_mock():  # type: ignore[no-untyped-def]
    from django.core.mail import EmailMultiAlternatives
    with mock.patch.object(EmailMultiAlternatives, 'send'):
        yield


@contextmanager
def gcs_client_mock():  # type: ignore[no-untyped-def]
    from google.cloud import storage as google_storage
    from collections import namedtuple

    File = namedtuple('File', ['name'])

    class DummyGCSBlob:
        def __init__(self, bucket_name, key, is_json):  # type: ignore[no-untyped-def]
            self.key = key
            self.bucket_name = bucket_name
            self.name = f"{bucket_name}/{key}"
            self.is_json = is_json
        def download_as_string(self):  # type: ignore[no-untyped-def]
            data = f'test_blob_{self.key}'
            if self.is_json:
                return json.dumps({'str_field': data, 'int_field': 123, 'dict_field': {'one': 'wow', 'two': 456}})
            return data
        def upload_from_string(self, string):  # type: ignore[no-untyped-def]
            print(f'String {string} uploaded to bucket {self.bucket_name}')
        def generate_signed_url(self, **kwargs):  # type: ignore[no-untyped-def]
            return f'https://storage.googleapis.com/{self.bucket_name}/{self.key}'
        def download_as_bytes(self):  # type: ignore[no-untyped-def]
            data = f'test_blob_{self.key}'
            if self.is_json:
                return json.dumps({'str_field': data, 'int_field': 123, 'dict_field': {'one': 'wow', 'two': 456}})
            return data

    class DummyGCSBucket:
        def __init__(self, bucket_name, is_json, **kwargs):  # type: ignore[no-untyped-def]
            self.name = bucket_name
            self.is_json = is_json
        def list_blobs(self, prefix):  # type: ignore[no-untyped-def]
            return [File('abc'), File('def'), File('ghi')]
        def blob(self, key):  # type: ignore[no-untyped-def]
            return DummyGCSBlob(self.name, key, self.is_json)  # type: ignore[no-untyped-call]

    class DummyGCSClient():
        def get_bucket(self, bucket_name):  # type: ignore[no-untyped-def]
            is_json = bucket_name.endswith('_JSON')
            return DummyGCSBucket(bucket_name, is_json)  # type: ignore[no-untyped-call]

        def list_blobs(self, bucket_name, prefix):  # type: ignore[no-untyped-def]
            is_json = bucket_name.endswith('_JSON')
            return [DummyGCSBlob(bucket_name, 'abc', is_json),  # type: ignore[no-untyped-call]
                    DummyGCSBlob(bucket_name, 'def', is_json),  # type: ignore[no-untyped-call]
                    DummyGCSBlob(bucket_name, 'ghi', is_json)]  # type: ignore[no-untyped-call]

    with mock.patch.object(google_storage, 'Client', return_value=DummyGCSClient()):
        yield


@contextmanager
def azure_client_mock():  # type: ignore[no-untyped-def]
    from io_storages.azure_blob import models 
    from collections import namedtuple

    File = namedtuple('File', ['name'])

    class DummyAzureBlob:
        def __init__(self, container_name, key):  # type: ignore[no-untyped-def]
            self.key = key
            self.container_name = container_name
        def download_as_string(self):  # type: ignore[no-untyped-def]
            return f'test_blob_{self.key}'
        def upload_blob(self, string, overwrite):  # type: ignore[no-untyped-def]
            print(f'String {string} uploaded to bucket {self.container_name}')
        def generate_signed_url(self, **kwargs):  # type: ignore[no-untyped-def]
            return f'https://storage.googleapis.com/{self.container_name}/{self.key}'

    class DummyAzureContainer:
        def __init__(self, container_name, **kwargs):  # type: ignore[no-untyped-def]
            self.name = container_name
        def list_blobs(self, name_starts_with):  # type: ignore[no-untyped-def]
            return [File('abc'), File('def'), File('ghi')]
        def get_blob_client(self, key):  # type: ignore[no-untyped-def]
            return DummyAzureBlob(self.name, key)  # type: ignore[no-untyped-call]
        def get_container_properties(self, **kwargs):  # type: ignore[no-untyped-def]
            return SimpleNamespace(
                name='test-container',
                last_modified='2022-01-01 01:01:01',
                etag='test-etag',
                lease='test-lease',
                public_access='public',
                has_immutability_policy=True,
                has_legal_hold=True,
                immutable_storage_with_versioning_enabled=True,
                metadata={'key': 'value'},
                encryption_scope='test-scope',
                deleted=False,
                version='1.0.0'
            )


    class DummyAzureClient():
        def get_container_client(self, container_name):  # type: ignore[no-untyped-def]
            return DummyAzureContainer(container_name)  # type: ignore[no-untyped-call]

    # def dummy_generate_blob_sas(*args, **kwargs):
    #     return 'token'

    with mock.patch.object(models.BlobServiceClient, 'from_connection_string', return_value=DummyAzureClient()):  # type: ignore[attr-defined]
        with mock.patch.object(models, 'generate_blob_sas', return_value='token'):
            yield


@contextmanager
def redis_client_mock():  # type: ignore[no-untyped-def]
    from fakeredis import FakeRedis  # type: ignore[import]
    from io_storages.redis.models import RedisStorageMixin

    redis = FakeRedis()
    # TODO: add mocked redis data

    with mock.patch.object(RedisStorageMixin, 'get_redis_connection', return_value=redis):
        yield


def upload_data(client, project, tasks):  # type: ignore[no-untyped-def]
    tasks = TaskWithAnnotationsSerializer(tasks, many=True).data  # type: ignore[no-untyped-call]
    data = [{'data': task['data'], 'annotations': task['annotations']} for task in tasks]
    return client.post(f'/api/projects/{project.id}/tasks/bulk', data=data, content_type='application/json')


def make_project(config, user, use_ml_backend=True, team_id=None, org=None):  # type: ignore[no-untyped-def]
    if org is None:
        org = Organization.objects.filter(created_by=user).first()
    project = Project.objects.create(created_by=user, organization=org, **config)
    if use_ml_backend:
        MLBackend.objects.create(project=project, url='http://localhost:8999')

    return project


@pytest.fixture
@pytest.mark.django_db
def project_id(business_client):  # type: ignore[no-untyped-def]
    payload = dict(title="test_project")
    response = business_client.post(
        "/api/projects/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    return response.json()["id"]


def make_task(config, project):  # type: ignore[no-untyped-def]
    from tasks.models import Task

    return Task.objects.create(project=project, overlap=project.maximum_annotations, **config)


def create_business(user):  # type: ignore[no-untyped-def]
    return None


def make_annotation(config, task_id):  # type: ignore[no-untyped-def]
    from tasks.models import Annotation, Task
    task = Task.objects.get(pk=task_id)

    return Annotation.objects.create(project_id=task.project_id, task_id=task_id, **config)


def make_prediction(config, task_id):  # type: ignore[no-untyped-def]
    from tasks.models import Prediction

    return Prediction.objects.create(task_id=task_id, **config)


def make_annotator(config, project, login=False, client=None):  # type: ignore[no-untyped-def]
    from users.models import User

    user = User.objects.create(**config)
    user.set_password('12345')
    user.save()

    create_business(user)  # type: ignore[no-untyped-call]

    if login:
        Organization.create_organization(created_by=user, title=user.first_name)  # type: ignore[no-untyped-call]

        if client is None:
            client = Client()
        signin_status_code = signin(client, config['email'], '12345').status_code  # type: ignore[no-untyped-call]
        assert signin_status_code == 302, f'Sign-in status code: {signin_status_code}'

    project.add_collaborator(user)
    if login:
        client.annotator = user
        return client
    return user


def invite_client_to_project(client, project):  # type: ignore[no-untyped-def]
    if apps.is_installed('annotators'):
        return client.get(f'/annotator/invites/{project.token}/')
    else:
        return SimpleNamespace(status_code=200)


def login(client, email, password):  # type: ignore[no-untyped-def]
    if User.objects.filter(email=email).exists():
        r = client.post(f'/user/login/', data={'email': email, 'password': password})
        assert r.status_code == 302, r.status_code
    else:
        r = client.post(f'/user/signup/', data={'email': email, 'password': password, 'title': 'Whatever'})
        assert r.status_code == 302, r.status_code


def signin(client, email, password):  # type: ignore[no-untyped-def]
    return client.post(f'/user/login/', data={'email': email, 'password': password})


def _client_is_annotator(client):  # type: ignore[no-untyped-def]
    return 'annotator' in client.user.email


def save_response(response):  # type: ignore[no-untyped-def]
    fp = os.path.join(settings.TEST_DATA_ROOT, 'tavern-output.json')
    with open(fp, 'w') as f:
        json.dump(response.json(), f)


def os_independent_path(_, path, add_tempdir=False):  # type: ignore[no-untyped-def]
    os_independent_path = Path(path)
    if add_tempdir:
        tempdir = Path(tempfile.gettempdir())
        os_independent_path = tempdir / os_independent_path

    os_independent_path_parent = os_independent_path.parent
    return Box(
        {
            'os_independent_path': str(os_independent_path),
            'os_independent_path_parent': str(os_independent_path_parent),
            'os_independent_path_tmpdir': str(Path(tempfile.gettempdir())),
        }
    )


def verify_docs(response):  # type: ignore[no-untyped-def]
    for _, path in response.json()['paths'].items():
        print(path)
        for _, method in path.items():
            print(method)
            if isinstance(method, dict):
                assert 'api' not in method['tags'], f'Need docs for API method {method}'


def empty_list(response):  # type: ignore[no-untyped-def]
    assert len(response.json()) == 0, f'Response should be empty, but is {response.json()}'


def save_export_file_path(response):  # type: ignore[no-untyped-def]
    export_id = response.json().get('id')
    export = Export.objects.get(id=export_id)
    file_path = export.file.path
    return Box({'file_path': file_path})


def save_convert_file_path(response, export_id=None):  # type: ignore[no-untyped-def]
    export = response.json()[0]
    convert = export['converted_formats'][0]


    converted = ConvertedFormat.objects.get(id=convert['id'])

    dir_path = os.path.join(settings.MEDIA_ROOT, settings.DELAYED_EXPORT_DIR)
    files = os.listdir(dir_path)
    try:
        file_path = converted.file.path
        return Box({'convert_file_path': file_path})
    except ValueError:
        return Box({'convert_file_path': None})


def file_exists_in_storage(response, exists=True, file_path=None):  # type: ignore[no-untyped-def]
    if not file_path:
        export_id = response.json().get('id')
        export = Export.objects.get(id=export_id)
        file_path = export.file.path

    assert os.path.isfile(file_path) == exists
