"""Contract tests for Clark error envelope parsing.

/rest routes answer with the monolith envelope {error_code, message};
the report route answers with FastAPI {"detail": ...};
scanyon 429 body carries {"detail", "reasons"}.
"""
import pytest
import responses
import requests

from mdast_cli_core.microservices import extract_error_message

pytestmark = pytest.mark.contract

URL = 'https://stand.example/x'


def _resp(mocked_responses, **kwargs):
    mocked_responses.add(responses.GET, URL, **kwargs)
    return requests.get(URL)


def test_monolith_envelope(mocked_responses):
    message = extract_error_message(_resp(
        mocked_responses, status=413,
        json={'error_code': 'file_too_large', 'message': 'File exceeds 500 MB limit'}))
    assert message == 'file_too_large: File exceeds 500 MB limit'


def test_fastapi_detail_string(mocked_responses):
    message = extract_error_message(_resp(
        mocked_responses, status=409, json={'detail': 'scan is not finished'}))
    assert message == 'scan is not finished'


def test_fastapi_detail_validation_list(mocked_responses):
    message = extract_error_message(_resp(
        mocked_responses, status=422,
        json={'detail': [{'loc': ['body', 'md5'], 'msg': 'field required'}]}))
    assert 'field required' in message


def test_429_reasons_preserved(mocked_responses):
    message = extract_error_message(_resp(
        mocked_responses, status=429,
        json={'detail': 'Scan limit exceeded', 'reasons': [{'limit': 'scans_per_day'}]}))
    assert 'Scan limit exceeded' in message
    assert 'scans_per_day' in message


def test_non_json_body(mocked_responses):
    message = extract_error_message(_resp(mocked_responses, status=502, body='Bad Gateway'))
    assert message == 'Bad Gateway'
