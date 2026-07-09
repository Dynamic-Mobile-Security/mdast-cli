"""Unit tests for the shared report-target resolver (used by both installations)."""
from types import SimpleNamespace

import pytest

from mdast_cli.helpers.helpers import resolve_report_targets

pytestmark = pytest.mark.unit


def args(report_format=None, pdf=None, json=None):
    return SimpleNamespace(report_format=report_format,
                           pdf_report_file_name=pdf,
                           summary_report_json_file_name=json)


def test_default_is_pdf_named_by_scan_id():
    assert resolve_report_targets(args(), 77) == {'pdf': 'scan_report_77.pdf'}


def test_format_json_only():
    assert resolve_report_targets(args(report_format='json'), 77) == {'json': 'scan_report_77.json'}


def test_format_all_produces_both():
    assert resolve_report_targets(args(report_format='all'), 77) == {
        'pdf': 'scan_report_77.pdf', 'json': 'scan_report_77.json'}


def test_format_none_produces_nothing():
    assert resolve_report_targets(args(report_format='none'), 77) == {}


def test_explicit_pdf_name_only():
    assert resolve_report_targets(args(pdf='r'), 77) == {'pdf': 'r.pdf'}


def test_explicit_json_name_does_not_pull_in_default_pdf():
    # regression: a defaulted 'pdf' format must not sneak a PDF in when the user
    # asked only for a JSON file by name.
    assert resolve_report_targets(args(json='r'), 77) == {'json': 'r.json'}


def test_extension_added_only_when_missing():
    assert resolve_report_targets(args(pdf='r.pdf', json='r.json'), 77) == {
        'pdf': 'r.pdf', 'json': 'r.json'}


def test_format_flag_adds_other_format_to_explicit_name():
    assert resolve_report_targets(args(report_format='all', pdf='p'), 77) == {
        'pdf': 'p.pdf', 'json': 'scan_report_77.json'}


def test_explicit_name_wins_over_none():
    assert resolve_report_targets(args(report_format='none', pdf='p'), 77) == {'pdf': 'p.pdf'}
