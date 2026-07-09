import hashlib
import os


def get_app_path(test_app_path):
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, test_app_path)
    return path


def check_app_md5(file_path):
    with open(f'{file_path}', "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def resolve_report_targets(arguments, scan_id):
    """Decide which reports to produce and to which files, for BOTH installations.

    The report format is selected by ``--report_format`` (``pdf`` by default, so a
    plain scan always yields a PDF). Precedence rules, kept identical for the
    monolith and the microservices flow:

      * an explicit ``--pdf_report_file_name`` / ``--summary_report_json_file_name``
        always produces that format at that path (backward compatible);
      * ``--report_format`` still applies on top, so ``--report_format all`` plus a
        PDF file name yields the JSON report too (at a default name);
      * with no file-name flags, ``--report_format`` alone decides
        (``pdf`` | ``json`` | ``all`` | ``none``);
      * default file names are derived from the scan id
        (``scan_report_<scan_id>.pdf`` / ``.json``) so a report can never land at
        a confusing server- or arg-derived name.

    Returns an ordered dict ``{'pdf': path, 'json': path}`` limited to the formats
    that should be produced. PDF is inserted first (it is the primary artifact).
    """
    pdf_name = arguments.pdf_report_file_name
    json_name = arguments.summary_report_json_file_name
    fmt = getattr(arguments, 'report_format', None)

    if pdf_name or json_name:
        want_pdf = bool(pdf_name)
        want_json = bool(json_name)
        if fmt in ('pdf', 'all'):
            want_pdf = True
        if fmt in ('json', 'all'):
            want_json = True
    else:
        effective = fmt or 'pdf'  # nothing specified -> default PDF
        want_pdf = effective in ('pdf', 'all')
        want_json = effective in ('json', 'all')

    targets = {}
    if want_pdf:
        target = pdf_name or f'scan_report_{scan_id}.pdf'
        # case-insensitive suffix check so report.PDF does not become report.PDF.pdf
        targets['pdf'] = target if target.lower().endswith('.pdf') else f'{target}.pdf'
    if want_json:
        target = json_name or f'scan_report_{scan_id}.json'
        targets['json'] = target if target.lower().endswith('.json') else f'{target}.json'
    return targets
