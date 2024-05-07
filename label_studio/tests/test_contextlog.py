"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import json
import pytest
import responses 
from django.test import override_settings


@pytest.mark.django_db
@responses.activate
@override_settings(CONTEXTLOG_SYNC=True)
def test_contextlog(business_client):
    responses.add(
        responses.POST,
        "https://tele.labelstud.io",
        json={"ok": "true"},
        status=201,
    )
    r = business_client.get('/api/users/')

    responses.assert_call_count("https://tele.labelstud.io", 1)
    assert responses.calls
    assert r.status_code == 200
    assert "env" not in json.loads(responses.calls[0].request.body)
